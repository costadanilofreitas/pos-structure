# -*- coding: utf-8 -*-

import ctypes
import os
import pickle
import platform

from cache import CacheManager, PeriodBasedExpiration
from persistence import Driver


class FingerPrintReader(object):
    def __init__(self):
        pass

    def enroll_user(self, user_id, pos_id, replace):
        pass

    def authenticate(self, pos_id):
        pass


class EnrolledUsersRepository(object):
    def __init__(self):
        pass

    def load_all_enrolled_users(self):
        raise NotImplementedError()

    def save_enrolled_user(self, enrolled_user, pos_id):
        raise NotImplementedError()

    def remove_enrolled_user(self, enrolled_user, pos_id):
        raise NotImplementedError()


class ObjectFileEnrolledUsersRepository(EnrolledUsersRepository):
    FINGER_PRINT_DATA_FILE = "finger_print_data_file.obj"

    def __init__(self):
        super(ObjectFileEnrolledUsersRepository, self).__init__()
        self.enrolled_users = []

    def load_all_enrolled_users(self):
        if not self.enrolled_users:
            if os.path.isfile(ObjectFileEnrolledUsersRepository.FINGER_PRINT_DATA_FILE):
                with open(ObjectFileEnrolledUsersRepository.FINGER_PRINT_DATA_FILE, "rb") as file:
                    self.enrolled_users = pickle.load(file)

        return self.enrolled_users

    def save_enrolled_user(self, enrolled_user, _):
        self.enrolled_users.append(enrolled_user)

        with open(ObjectFileEnrolledUsersRepository.FINGER_PRINT_DATA_FILE, "wb") as file:
            pickle.dump(self.enrolled_users, file)

    def remove_enrolled_user(self, enrolled_user, _):
        for already_enrolled_user in self.enrolled_users:
            if already_enrolled_user.user_id == enrolled_user.user_id:
                self.enrolled_users.remove(already_enrolled_user)
                break

        with open(ObjectFileEnrolledUsersRepository.FINGER_PRINT_DATA_FILE, "wb") as file:
            pickle.dump(self.enrolled_users, file)


class DatabaseEnrolledUsersRepository(EnrolledUsersRepository):
    def __init__(self, mbcontext, enrolled_users_expiration):
        # type: (MBEasyContext) -> None
        super(DatabaseEnrolledUsersRepository, self).__init__()
        self.mbcontext = mbcontext
        self.enrolled_users = []
        self.enrolled_users_cache = CacheManager(PeriodBasedExpiration(enrolled_users_expiration), threaded=False)

    def load_all_enrolled_users(self):
        return self.enrolled_users_cache.get_cached_object(self._renew_enrolled_users_cache)

    def save_enrolled_user(self, enrolled_user, pos_id):
        conn = None
        try:
            conn = Driver().open(self.mbcontext, dbname=str(pos_id))
            conn.query("update Users set FingerPrintMinutiae = x'%s' where UserId = %s" % (enrolled_user.fmd_buffer.encode("hex"), enrolled_user.user_id))
        finally:
            if conn:
                conn.close()

        self.enrolled_users.append(enrolled_user)

    def remove_enrolled_user(self, enrolled_user, pos_id):
        conn = None
        try:
            conn = Driver().open(self.mbcontext, dbname=str(pos_id))
            conn.query("update Users set FingerPrintMinutiae = NULL where UserId = %s" % enrolled_user.user_id)
        finally:
            if conn:
                conn.close()

        for already_enrolled_user in self.enrolled_users:
            if already_enrolled_user.user_id == enrolled_user.user_id:
                self.enrolled_users.remove(already_enrolled_user)
                break

    def _renew_enrolled_users_cache(self):
        conn = None
        try:
            conn = Driver().open(self.mbcontext)
            saved_minutiaes = [(x.get_entry(0), x.get_entry(1)) for x in conn.select("select UserId, hex(FingerPrintMinutiae) from Users where FingerPrintMinutiae is not null")]
            self.enrolled_users = []
            for saved_minutiae in saved_minutiaes:
                fmd_data = bytes(bytearray.fromhex(saved_minutiae[1]))
                enrolled_user = User(saved_minutiae[0], len(fmd_data), fmd_data)
                self.enrolled_users.append(enrolled_user)
        finally:
            if conn:
                conn.close()

        return self.enrolled_users


class User:
    def __init__(self, user_id, fmd_buffer_size, fmd_buffer):
        self.user_id = user_id
        self.fmd_buffer_size = fmd_buffer_size
        self.fmd_buffer = fmd_buffer


class DigitalPersonaFingerPrintReader(FingerPrintReader):
    DPFPDD_SUCCESS = 0
    DPFPDD_E_MORE_DATA = 0x0d

    DPFJ_SUCCESS = 0
    DPFJ_E_MORE_DATA = 0xd
    DPFJ_E_INVALID_FID = 0x65

    MAX_DEVICE_NAME_LENGTH = 1024
    MAX_STR_LENGTH = 128

    DPFJ_FMD_ANSI_378_2004 = 0x001B0001

    DPFPDD_IMG_FMT_PIXEL_BUFFER = 0
    DPFPDD_IMG_PROC_DEFAULT = 0
    DPFPDD_QUALITY_GOOD = 0

    DPFJ_POSITION_RINDEX = 2

    DPFPDD_STATUS_READY = 0
    DPFPDD_STATUS_FAILURE = 3

    # Events
    EVT_PLACE_FINGER_LOGIN = "EVT_PLACE_FINGER_LOGIN"
    EVT_PLACE_FINGER_AUTHORIZATION = "EVT_PLACE_FINGER_AUTHORIZATION"
    EVT_PLACE_RIGHT_INDEX_FINGER = "EVT_PLACE_RIGHT_INDEX_FINGER"
    EVT_PLACE_LEFT_INDEX_FINGER = "EVT_PLACE_LEFT_INDEX_FINGER"
    EVT_BAD_FINGERPRINT_READ = "EVT_BAD_FINGERPRINT_READ"
    EVT_FINGER_ALREADY_REGISTERED = "EVT_FINGER_ALREADY_REGISTERED"
    EVT_ENROLLMENT_SUCCESS = "EVT_ENROLLMENT_SUCCESS"
    EVT_CLOSE_ALL_DIALOGS = "EVT_CLOSE_ALL_DIALOGS"
    EVT_FINGER_READ_SUCCESSFULLY_READ_AGAIN = "EVT_FINGER_READ_SUCCESSFULLY_READ_AGAIN"

    def __init__(self, enrolled_users_repository, call_back, threshold, finger_print_timeout, module_directory):
        # type: (EnrolledUsersRepository, FingerPrintReaderCallback) -> None
        super(DigitalPersonaFingerPrintReader, self).__init__()
        self.call_back = call_back
        self.enrolled_users_repository = enrolled_users_repository
        self.threshold = threshold
        self.finger_print_timeout = finger_print_timeout
        self.module_directory = module_directory

        bits = platform.architecture()[0]
        if bits == "32bit":
            dll_directory = os.path.join(os.path.abspath(self.module_directory), "x32")
        else:
            dll_directory = os.path.join(os.path.abspath(self.module_directory), "x64")

        self.dpfpdd = ctypes.WinDLL(os.path.join(dll_directory, "dpfpdd.dll"))
        self.dpfj = ctypes.WinDLL(os.path.join(dll_directory, "dpfj.dll"))

        self.dpfpdd_init = self.dpfpdd["dpfpdd_init"]

        self.dpfpdd_exit = self.dpfpdd["dpfpdd_exit"]

        self.dpfpdd_version = self.dpfpdd["dpfpdd_version"]
        self.dpfpdd_version.argtypes = [ctypes.POINTER(DfpddVersion)]
        self.dpfpdd_version.restype = ctypes.c_int

        self.dpfpdd_query_devices = self.dpfpdd["dpfpdd_query_devices"]
        self.dpfpdd_query_devices.argtypes = [ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(DpfpddDevInfo)]
        self.dpfpdd_query_devices.restype = ctypes.c_int

        self.dpfpdd_open = self.dpfpdd["dpfpdd_open"]
        self.dpfpdd_open.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_void_p)]
        self.dpfpdd_open.restype = ctypes.c_int

        self.dpfpdd_close = self.dpfpdd["dpfpdd_close"]
        self.dpfpdd_close.argtypes = [ctypes.c_void_p]
        self.dpfpdd_close.restype = ctypes.c_int

        self.dpfpdd_get_device_status = self.dpfpdd["dpfpdd_get_device_status"]
        self.dpfpdd_get_device_status.argtypes = [ctypes.c_void_p, ctypes.POINTER(DpfpddDevStatus)]
        self.dpfpdd_get_device_status.restype = ctypes.c_int

        self.dpfj_start_enrollment = self.dpfj["dpfj_start_enrollment"]
        self.dpfj_start_enrollment.argtypes = [ctypes.c_void_p]
        self.dpfj_start_enrollment.restype = ctypes.c_int

        self.dpfpdd_capture = self.dpfpdd["dpfpdd_capture"]
        self.dpfpdd_capture.argtypes = [ctypes.c_void_p, ctypes.POINTER(DpfpddCaptureParam), ctypes.c_uint, ctypes.POINTER(DpfpddCaptureResult), ctypes.POINTER(ctypes.c_uint), ctypes.c_char_p]
        self.dpfpdd_capture.restype = ctypes.c_int

        self.dpfj_create_fmd_from_raw = self.dpfj["dpfj_create_fmd_from_raw"]
        self.dpfj_create_fmd_from_raw.argtypes = [ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint)]
        self.dpfj_create_fmd_from_raw.restype = ctypes.c_int

        self.dpfj_add_to_enrollment = self.dpfj["dpfj_add_to_enrollment"]
        self.dpfj_add_to_enrollment.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint]
        self.dpfj_add_to_enrollment.restype = ctypes.c_int

        self.dpfj_create_enrollment_fmd = self.dpfj["dpfj_create_enrollment_fmd"]
        self.dpfj_create_enrollment_fmd.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint)]
        self.dpfj_create_enrollment_fmd.restype = ctypes.c_int

        self.dpfj_finish_enrollment = self.dpfj["dpfj_finish_enrollment"]
        self.dpfj_finish_enrollment.argtypes = []
        self.dpfj_finish_enrollment.restype = ctypes.c_int

        self.dpfj_identify = self.dpfj["dpfj_identify"]
        self.dpfj_identify.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_uint), ctypes.c_uint, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(DpfjCandidate)]
        self.dpfj_identify.restype = ctypes.c_int

    def enroll_user(self, user_id, pos_id, replace):
        p_device = self._init_device()

        try:
            ret = self.dpfj_start_enrollment(DigitalPersonaFingerPrintReader.DPFJ_FMD_ANSI_378_2004)
            if ret != DigitalPersonaFingerPrintReader.DPFJ_SUCCESS:
                raise DigitalPersonaFingerPrintException(ret, "Error calling dpfj_start_enrollment")

            try:
                self.call_back.finger_print_reader_callback(
                    DigitalPersonaFingerPrintReader.EVT_PLACE_RIGHT_INDEX_FINGER, pos_id)
                finish = False
                attempt = 1
                while not finish:
                    try:
                        fmd_buffer_size, fmd_buffer = self._capture_fmd(p_device)
                    except DigitalPersonaFingerPrintException as ex:
                        if ex.error_code & 0xFFFF == DigitalPersonaFingerPrintReader.DPFJ_E_INVALID_FID:
                            self.call_back.finger_print_reader_callback(
                                DigitalPersonaFingerPrintReader.EVT_BAD_FINGERPRINT_READ, pos_id)
                            continue
                        else:
                            raise ex

                    show_error = False
                    identified_user_id = self._identify_fmd(p_device, fmd_buffer_size, fmd_buffer)
                    if replace and identified_user_id is not None and identified_user_id != user_id:
                        show_error = True
                    elif not replace and identified_user_id is not None:
                        show_error = True

                    if show_error:
                        self.call_back.finger_print_reader_callback(
                            DigitalPersonaFingerPrintReader.EVT_FINGER_ALREADY_REGISTERED, pos_id)
                        raise DigitalPersonaFingerPrintException(-1, "Fingerprint already present in the database")

                    ret = self.dpfj_add_to_enrollment(DigitalPersonaFingerPrintReader.DPFJ_FMD_ANSI_378_2004, fmd_buffer, fmd_buffer_size, 0)
                    if ret & 0xFF == DigitalPersonaFingerPrintReader.DPFJ_SUCCESS:
                        finish = True
                    elif ret & 0xFF != DigitalPersonaFingerPrintReader.DPFJ_E_MORE_DATA:
                        raise DigitalPersonaFingerPrintException(ret, "Error calling dpfj_add_to_enrollment")
                    else:
                        self.call_back.finger_print_reader_callback(
                            DigitalPersonaFingerPrintReader.EVT_FINGER_READ_SUCCESSFULLY_READ_AGAIN, pos_id, attempt)

                    attempt += 1

                fmd_buffer_size = ctypes.c_uint(2500)
                fmd_buffer = ctypes.create_string_buffer(fmd_buffer_size.value)
                ret = self.dpfj_create_enrollment_fmd(fmd_buffer, ctypes.pointer(fmd_buffer_size))
                if ret != DigitalPersonaFingerPrintReader.DPFJ_SUCCESS:
                    raise DigitalPersonaFingerPrintException(ret, "Error calling dpfj_create_enrollment_fmd")
            finally:
                ret = self.dpfj_finish_enrollment()
                if ret != DigitalPersonaFingerPrintReader.DPFJ_SUCCESS:
                    raise DigitalPersonaFingerPrintException(ret, "Error calling dpfj_finish_enrollment")

            fmd_buffer_correct_size = bytearray()
            for i in range(0, fmd_buffer_size.value, 1):
                fmd_buffer_correct_size.append(fmd_buffer[i])
            fmd_buffer_correct_size = bytes(fmd_buffer_correct_size)

            enrolled_user = User(user_id, fmd_buffer_size.value, fmd_buffer_correct_size)

            if replace:
                self.enrolled_users_repository.remove_enrolled_user(enrolled_user, pos_id)

            self.enrolled_users_repository.save_enrolled_user(enrolled_user, pos_id)

            self.call_back.finger_print_reader_callback(DigitalPersonaFingerPrintReader.EVT_ENROLLMENT_SUCCESS, pos_id)

            return enrolled_user.fmd_buffer
        except Exception as ex:
            if ex is not DigitalPersonaFingerPrintException or ex.error_code not in [-1]:
                self.call_back.finger_print_reader_callback(DigitalPersonaFingerPrintReader.EVT_CLOSE_ALL_DIALOGS, pos_id)

            raise ex
        finally:
            self._finish_device(p_device)

    def authenticate(self, pos_id, authorization=False):
        p_device = self._init_device()
        try:
            if authorization:
                self.call_back.finger_print_reader_callback(DigitalPersonaFingerPrintReader.EVT_PLACE_FINGER_AUTHORIZATION, pos_id)
            else:
                self.call_back.finger_print_reader_callback(DigitalPersonaFingerPrintReader.EVT_PLACE_FINGER_LOGIN, pos_id)
            fmd_buffer_size, fmd_buffer = self._capture_fmd(p_device)

            user_id = self._identify_fmd(p_device, fmd_buffer_size, fmd_buffer)

            return user_id
        finally:
            self.call_back.finger_print_reader_callback(DigitalPersonaFingerPrintReader.EVT_CLOSE_ALL_DIALOGS, pos_id)
            self._finish_device(p_device)

    def check_device(self):
        p_device = self._init_device()

        try:
            device_status = DpfpddDevStatus()
            device_status.size = ctypes.sizeof(DpfpddDevStatus)
            device_status_pointer = ctypes.pointer(device_status)

            ret = self.dpfpdd_get_device_status(p_device.contents.value, device_status_pointer)
            if ret != DigitalPersonaFingerPrintReader.DPFPDD_SUCCESS:
                raise DigitalPersonaFingerPrintException(ret, "Error calling dpfpdd_get_device_status")

            if device_status.status != DigitalPersonaFingerPrintReader.DPFPDD_STATUS_READY:
                raise DigitalPersonaFingerPrintException(-3, "Device failure: {0}".format(device_status.status))

        finally:
            self._finish_device(p_device)

    def _init_device(self):
        ret = self.dpfpdd_init()
        if ret != DigitalPersonaFingerPrintReader.DPFPDD_SUCCESS:
            raise DigitalPersonaFingerPrintException(ret, "Error calling dpfpdd_init")

        version = DfpddVersion()
        version.size = ctypes.sizeof(DfpddVersion)

        cnt_devices = ctypes.c_uint(0)
        ret = self.dpfpdd_query_devices(ctypes.pointer(cnt_devices), None)
        if ret & 0xFF != DigitalPersonaFingerPrintReader.DPFPDD_E_MORE_DATA:
            raise DigitalPersonaFingerPrintException(ret, "Error calling dpfpdd_query_devices")
        else:
            devInfo = DpfpddDevInfo()
            devInfo.size = ctypes.sizeof(DpfpddDevInfo)
            ret = self.dpfpdd_query_devices(ctypes.pointer(cnt_devices), ctypes.pointer(devInfo))
            if ret == DigitalPersonaFingerPrintReader.DPFPDD_SUCCESS:
                # Device found
                p_device = ctypes.pointer(ctypes.c_void_p(0))
                ret = self.dpfpdd_open(devInfo.name, p_device)
                if ret != 0:
                    raise DigitalPersonaFingerPrintException(ret, "Error calling dpfpdd_open")
            else:
                raise Exception(ret, "Error calling dpfpdd_query_devices")

        return p_device

    def _finish_device(self, p_device):
        ret = self.dpfpdd_close(p_device.contents.value)
        if ret != DigitalPersonaFingerPrintReader.DPFPDD_SUCCESS:
            raise DigitalPersonaFingerPrintException(ret, "Error calling dpfpdd_close")

        ret = self.dpfpdd_exit()
        if ret != DigitalPersonaFingerPrintReader.DPFPDD_SUCCESS:
            raise DigitalPersonaFingerPrintException(ret, "Error calling dpfpdd_exit")

    def _capture_fmd(self, p_device):
        dev_capture_param = DpfpddCaptureParam()
        dev_capture_param.size = ctypes.sizeof(DpfpddCaptureParam)
        dev_capture_param.img_fmt = DigitalPersonaFingerPrintReader.DPFPDD_IMG_FMT_PIXEL_BUFFER
        dev_capture_param.image_proc = DigitalPersonaFingerPrintReader.DPFPDD_IMG_PROC_DEFAULT
        dev_capture_param.image_res = 500

        dev_capture_result = DpfpddCaptureResult()
        dev_capture_result.size = ctypes.sizeof(DpfpddCaptureResult)

        buffer_size = ctypes.c_uint(200000)
        image_buffer = ctypes.create_string_buffer(buffer_size.value)

        ret = self.dpfpdd_capture(p_device.contents.value,
                                  ctypes.pointer(dev_capture_param),
                                  self.finger_print_timeout,
                                  ctypes.pointer(dev_capture_result),
                                  ctypes.pointer(buffer_size),
                                  image_buffer)
        if ret != DigitalPersonaFingerPrintReader.DPFPDD_SUCCESS:
            raise DigitalPersonaFingerPrintException(ret, "Error calling dpfpdd_capture")

        if buffer_size.value == 200000:
            # Se o buffer nao foi modificado, saimos por timeout
            raise DigitalPersonaFingerPrintException(-2, "Timeout reading finferprint")

        fmd_buffer_size = ctypes.c_uint(2500)
        fmd_buffer = ctypes.create_string_buffer(fmd_buffer_size.value)
        ret = self.dpfj_create_fmd_from_raw(image_buffer,
                                            buffer_size,
                                            dev_capture_result.info.width,
                                            dev_capture_result.info.height,
                                            500,
                                            DigitalPersonaFingerPrintReader.DPFJ_POSITION_RINDEX,
                                            0,
                                            DigitalPersonaFingerPrintReader.DPFJ_FMD_ANSI_378_2004,
                                            fmd_buffer,
                                            fmd_buffer_size)
        if ret != DigitalPersonaFingerPrintReader.DPFJ_SUCCESS:
            raise DigitalPersonaFingerPrintException(ret, "Error calling dpfj_create_fmd_from_raw")

        return fmd_buffer_size, fmd_buffer

    def _identify_fmd(self, p_device, fmd_buffer_size, fmd_buffer):
        enrolled_users = self.enrolled_users_repository.load_all_enrolled_users()

        if len(enrolled_users) == 0:
            return None

        fmds_cnt = ctypes.c_uint(len(enrolled_users))
        fmds_data = (ctypes.c_char_p * fmds_cnt.value)()
        fmds_size = (ctypes.c_uint * fmds_cnt.value)()
        for i in range(0, fmds_cnt.value, 1):
            fmds_data[i] = ctypes.c_char_p(enrolled_users[i].fmd_buffer)
            fmds_size[i] = ctypes.c_uint(enrolled_users[i].fmd_buffer_size)

        candidate = DpfjCandidate()
        candidate.fmd_idx = 10
        candidate.size = ctypes.sizeof(DpfjCandidate) - 10
        candidates = ctypes.pointer(candidate)

        candidate_cnt = ctypes.pointer(ctypes.c_uint(1))
        ret = self.dpfj_identify(DigitalPersonaFingerPrintReader.DPFJ_FMD_ANSI_378_2004,
                                 fmd_buffer,
                                 fmd_buffer_size,
                                 ctypes.c_uint(0),
                                 DigitalPersonaFingerPrintReader.DPFJ_FMD_ANSI_378_2004,
                                 fmds_cnt,
                                 fmds_data,
                                 fmds_size,
                                 ctypes.c_uint(self.threshold),
                                 candidate_cnt,
                                 ctypes.cast(candidates, ctypes.POINTER(DpfjCandidate)))

        if ret != DigitalPersonaFingerPrintReader.DPFJ_SUCCESS:
            raise DigitalPersonaFingerPrintException(ret, "Error calling dpfj_identify")

        if candidate_cnt.contents.value == 0:
            return None

        return enrolled_users[candidates.contents.fmd_idx].user_id


class DigitalPersonaFingerPrintException(Exception):
    def __init__(self, error_code, message):
        super(DigitalPersonaFingerPrintException, self).__init__(message)
        self.error_code = error_code


class DfpddVerInfo(ctypes.Structure):
    _fields_ = [
        ('major', ctypes.c_int),
        ('minor', ctypes.c_int),
        ('maintenance', ctypes.c_int)
    ]


class DfpddVersion(ctypes.Structure):
    _fields_ = [
        ('size', ctypes.c_uint),
        ('lib_ver', DfpddVerInfo),
        ('api_ver', DfpddVerInfo)
    ]


class DpfpddHwDescr(ctypes.Structure):
    _fields_ = [
        ('vendor_name', ctypes.c_char * DigitalPersonaFingerPrintReader.MAX_STR_LENGTH),
        ('product_name', ctypes.c_char * DigitalPersonaFingerPrintReader.MAX_STR_LENGTH),
        ('serial_num', ctypes.c_char * DigitalPersonaFingerPrintReader.MAX_STR_LENGTH)
    ]


class DpfpddHwId(ctypes.Structure):
    _fields_ = [
        ('vendor_id', ctypes.c_ushort),
        ('product_id', ctypes.c_ushort)
    ]


class DpfpddHwVersion(ctypes.Structure):
    _fields_ = [
        ('hw_ver', DfpddVerInfo),
        ('fw_ver', DfpddVerInfo),
        ('bcd_rev', ctypes.c_ushort),
    ]


class DpfpddDevInfo(ctypes.Structure):
    _fields_ = [
        ('size', ctypes.c_uint),
        ('name', ctypes.c_char * DigitalPersonaFingerPrintReader.MAX_DEVICE_NAME_LENGTH),
        ('descr', DpfpddHwDescr),
        ('id', DpfpddHwId),
        ('ver', DpfpddHwVersion),
        ('modality', ctypes.c_uint),
        ('technology', ctypes.c_uint),
    ]


class DpfpddCaptureParam(ctypes.Structure):
    _fields_ = [
        ('size', ctypes.c_uint),
        ('image_fmt', ctypes.c_uint),
        ('image_proc', ctypes.c_uint),
        ('image_res', ctypes.c_uint)
    ]


class DpfpddImageInfo(ctypes.Structure):
    _fields_ = [
        ('size', ctypes.c_uint),
        ('width', ctypes.c_uint),
        ('height', ctypes.c_uint),
        ('res', ctypes.c_uint),
        ('bpp', ctypes.c_uint)
    ]


class DpfpddCaptureResult(ctypes.Structure):
    _fields_ = [
        ('size', ctypes.c_uint),
        ('success', ctypes.c_int),
        ('quality', ctypes.c_uint),
        ('score', ctypes.c_uint),
        ('info', DpfpddImageInfo)
    ]


class DpfjCandidate(ctypes.Structure):
    _fields_ = [
        ('size', ctypes.c_uint),
        ('fmd_idx', ctypes.c_uint),
        ('view_idx', ctypes.c_uint)
    ]


class DpfpddDevStatus(ctypes.Structure):
    _fields_ = [
        ('size', ctypes.c_uint),
        ('status', ctypes.c_uint),
        ('finger_detected', ctypes.c_uint),
        ('data', ctypes.c_byte)
    ]
