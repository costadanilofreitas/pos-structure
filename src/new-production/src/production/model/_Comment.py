from ._CustomStorage import CustomStorage


class Comment(CustomStorage):
    """ class Comment(object)
    Represents an item's comment
    """

    comment_id = ''
    text = ''

    def __init__(self, **kargs):
        CustomStorage.__init__(self)
        for key, val in kargs.iteritems():
            setattr(self, key, val)

    def __str__(self):
        return "Comment id={} text={}".format(self.comment_id, self.text)
