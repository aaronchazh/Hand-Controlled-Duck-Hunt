class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Rect(object):
    def __init__(self, p1, p2):
        '''Store the top, bottom, left and right values for points 
               p1 and p2 are the (corners) in either order
        '''
        self.left   = min(p1.x, p2.x)
        self.right  = max(p1.x, p2.x)
        self.bottom = min(p1.y, p2.y)
        self.top    = max(p1.y, p2.y)

def overlap(r1,r2):
    hoverlaps = True
    voverlaps = True
    if (r1.left > r2.right) or (r1.right < r2.left):
        hoverlaps = False
    if (r1.top < r2.bottom) or (r1.bottom > r2.top):
        voverlaps = False
    return hoverlaps and voverlaps
