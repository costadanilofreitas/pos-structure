# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\simplecsv.py
import csv
import cStringIO

def _rows_to_csv(rows, fp, delimiter, header, fields):
    """ _rows_to_csv(rows, fp, delimiter, header, fields)
    
        Converts a list of "objects" into a csv structure and writes
        contents to a file like object.
    
        @param rows: {[dict]} - List of "row" objects
        @param fp: {str} - File object
        @param delimiter: {str} - Character to use as delimiter
        @param header: {boolean} - Whether to write a header line in file
        @param fields: {[str]} - List of values to use as field names
    """
    if not rows:
        raise ValueError('Object list is empty')
    fieldnames = fields if fields else rows[0].keys()
    writer = csv.DictWriter(fp, fieldnames=fieldnames, delimiter=delimiter, extrasaction='ignore')
    if header:
        writer.writerow(dict(((f, f) for f in fieldnames)))
    writer.writerows(rows)


def dumps(objs, delimiter = ',', header = True, fields = []):
    """ dumps(objs, delimiter=',', header=True, fields=[])
    
        Converts a list of "objects" into a csv string.
    
        @param objs: {[dict]} - List of "row" objects
        @param delimiter: {str} - Character to use as delimiter
        @param header: {boolean} - Whether to write a header line in file
        @param fields: {[str]} - List of values to use as field names
        @return {str} - csv file contents
    """
    buf = cStringIO.StringIO()
    _rows_to_csv(objs, buf, delimiter=delimiter, header=header, fields=fields)
    s = buf.getvalue()
    buf.close()
    return s


def dump(objs, fp, delimiter = ',', header = True, fields = []):
    """ dump(objs, fp, delimiter=',', header=True, fields=[])
    
        Writes a list of "objects" to a csv file.
    
        @param objs: {[dict]} - List of "row" objects
        @param fp: {str} - File object
        @param delimiter: {str} - Character to use as delimiter
        @param header: {boolean} - Whether to write a header line in file
        @param fields: {[str]} - List of values to use as field names
    """
    _rows_to_csv(objs, fp, delimiter=delimiter, header=header, fields=fields)


def _csv_to_rows(fp, delimiter, header, fieldnames):
    """ _csv_to_rows(fp, delimiter, header, fieldnames)
    
        Converts a csv structured file to a list of "objects"
    
        @param fp: {str} - File object
        @param delimiter: {str} - Character to use as delimiter
        @param header: {boolean} - Whether to write a header line in file
        @param fieldnames: {[str]} - List of values to use as field names
    """
    reader = csv.reader(fp, delimiter=delimiter)
    fields = next(reader, []) if header else fieldnames
    rows = list(reader)
    if not fields:
        fields = [ 'field_%s' % r for r in range(1, len(rows[0]) + 1) ]
    objs = [ dict(zip(fields, row)) for row in rows ]
    return objs


def loads(s, delimiter = ',', header = True, fieldnames = []):
    """ loads(s, delimiter=',', header=True, fieldnames=[])
    
        Converts a csv structured string to a list of "objects"
    
        @param s: {str} - csv string contents
        @param delimiter: {str} - Character to use as delimiter
        @param header: {boolean} - Whether to write a header line in file
        @param fieldnames: {[str]} - List of values to use as field names
        @return {[dict]} - List of "row" objects
    """
    buf = cStringIO.StringIO(s)
    objs = _csv_to_rows(buf, delimiter=delimiter, header=header, fieldnames=fieldnames)
    buf.close()
    return objs


def load(fp, delimiter = ',', header = True, fieldnames = []):
    """ load(fp, delimiter=',', header=True, fieldnames=[])
    
        Converts a csv file to a list of "objects"
    
        @param fp: {str} - File object
        @param delimiter: {str} - Character to use as delimiter
        @param header: {boolean} - Whether to write a header line in file
        @param fieldnames: {[str]} - List of values to use as field names
        @return {[dict]} - List of "row" objects
    """
    objs = _csv_to_rows(fp, delimiter=delimiter, header=header, fieldnames=fieldnames)
    return objs