# encoding: utf-8
import os
import hvdriver
from mwposdriver import MwPosDriver
from selenium import webdriver
from msgbus import MBEasyContext


RamDiskPosDirectory = "D:\\Projects\\Burguer King\\mwpos"


def before_all(context):
    # Variáveis que precisam estar no environment para conseguimos utilizat o mbcontext
    os.environ["HVPORT"] = "14000"
    os.environ["HVIP"] = "127.0.0.1"
    os.environ["HVCOMPPORT"] = "35686"
    # Para simularmos um componente, temos que estar com o CWD no bin
    context.old_cwd = os.getcwd()
    bin_dir = os.path.abspath(RamDiskPosDirectory + "\\bin")
    os.chdir(bin_dir)

    hvdriver.HyperVisorComunicator().wait_persistence()

    context.mbcontext = MBEasyContext("E2ETest")


def after_all(context):
    os.chdir(context.old_cwd)
    context.mbcontext.MB_EasyFinalize()
