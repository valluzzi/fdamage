import boto3
from botocore.response import StreamingBody

# fdamage text format
f_example = """wd,dmg #header is optional
#0,0.0
0.5,0.25
1,0.4
1.5,0.5
2,0.6
3,0.75
# this is unvalid line
4,0.a
# this is a comment
5,0.95
# this is a unsorted line
7,1.0
6,1.0
9,-1.0
# this is a out of range damage percentage
8,1.2
"""


def parseFloat(x):
    """
    Parse float
    """
    try:
        return float(x)
    except ValueError:
        return None
    

def normalize_text(text):
    """
    Normalize text
    """
    if text is None:
        text = ""
    elif isinstance(text, str) and text.startswith("s3://"):
        s3 = boto3.client('s3')
        bucket, key = text.split('s3://')[1].split('/', 1)
        text = normalize_text(s3.get_object(Bucket=bucket, Key=key))
    elif isinstance(text, str):
        text = text.replace('\r\n', '\n').replace('\r', '\n')
    elif isinstance(text, bytes):
        text = normalize_text(text.decode('utf-8'))
    elif isinstance(text, StreamingBody):
        text = normalize_text(text.read())
    elif isinstance(text, dict) and "Body" in text:
        text = normalize_text(text["Body"])
    
    return text


def parse_fdamage(text):
    """
    parse fdamage text to list of couples
    """
    res =[]

    text = normalize_text(text)

    arr = text.split('\n')
    # exclude all lines that are not in the format of x,y
    arr = [line.split(',') for line in arr if len(line.split(',')) == 2]
    # parse all items to float
    res = [(parseFloat(x), parseFloat(y)) for x,y in arr]
    # exclude all items that are not in the format of x,y
    res = [(x,y) for x,y in res if x is not None and y is not None]
    # sort by x
    res = sorted(res, key=lambda x: x[0])

    # paranoid check
    # check that all x are positive, exclude all items that are not positive
    res = [(x,y) for x,y in res if x > 0 and y >= 0 and y <= 1.0]

    # add (0,0) to the beginning if it is not there
    if len(res) >0 and  res[0][0] != 0:
        res.insert(0, (0,0))

    return res


if __name__ == '__main__':
    text = f_example
    #arr = parse_fdamage(text)
    
    arr = parse_fdamage("s3://saferplaces.co/fdamage/shared/residential.csv")
    
    print(arr)
