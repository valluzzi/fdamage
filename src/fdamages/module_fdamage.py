import os
import boto3
import requests
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

def normpath(pathname):
    """
    normpath
    """
    if not pathname:
        return ""
    pathname = os.path.normpath(pathname.replace("\\", "/")).replace("\\", "/")
    pathname = pathname.replace(":/", "://") #patch for s3:// and http:// https://
    return pathname


def juststem(pathname):
    """
    juststem
    """
    pathname = os.path.basename(pathname)
    root, _ = os.path.splitext(pathname)
    return root


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
        try:
            s3 = boto3.client('s3')
            bucket, key = text.split('s3://')[1].split('/', 1)
            text = normalize_text(s3.get_object(Bucket=bucket, Key=key))
        except Exception:
            text = ""
    elif isinstance(text, str) and text.startswith("https://"):
        text = normalize_text(requests.get(text).text)
    elif isinstance(text, str):
        text = text.replace('\r\n', '\n').replace('\r', '\n')
    elif isinstance(text, bytes):
        text = normalize_text(text.decode('utf-8'))
    elif isinstance(text, StreamingBody):
        text = normalize_text(text.read())
    elif isinstance(text, dict) and "Body" in text:
        text = normalize_text(text["Body"])
    elif isinstance(text, (list,tuple)):
        text = "\n".join([f"{x},{y}" for x,y in text])
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

    # if some values is beetwen 0 and 100 convert to percentage
    convert_to_percentage = False
    for _,y in res:
        if y > 1 and y <= 100:
            convert_to_percentage = True
            break
    if convert_to_percentage:
        res = [(x, y/100) for x,y in res]
        
    # paranoid check
    # check that all x are positive, exclude all items that are not positive
    res = [(x,y) for x,y in res if x > 0 and y >= 0 and y <= 1]

    # add (0,0) to the beginning if it is not there
    if len(res) >0 and  res[0][0] != 0:
        res.insert(0, (0,0))

    return res


def list_fdamages(bucket="saferplaces.co", prefix ="fdamage/"):
    """
    List all fdamages
    """
    res =[]
    s3 = boto3.client('s3')
    # list all files using paginator to avoid limit of 1000 items list only folder fdamges
    paginator = s3.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for content in result.get('Contents', []):
            key = content['Key']
            if key.endswith(".csv"):
                res.append({
                    "name": juststem(key),
                    "value": key,
                    "custom": ("shared/" not in key)
                })
    return res


def upsert(key, arr):
    """
    Upsert fdamage
    """
    bucket="saferplaces.co"
    try:
        s3 = boto3.client('s3')
        arr = parse_fdamage(arr)
        text = "wd,dmg\n"+ "\n".join([f"{x},{y}" for x,y in arr])
        s3.put_object(Bucket=bucket, Key=key, Body=text)
        return {
            "name": juststem(key),
            "value": key,
            "custom": ("shared/" not in key)
        }
    except Exception as e:
        print(e)
        
    return None


def upsert_fdamage(name, arr, username=""):
    """
    Upsert user fdamage
    """
    if username == "":
        username = "shared"
    # TODO
    # check that the user key exists
    key = f"fdamage/{username}/{juststem(name)}.csv"
    return upsert(key, arr)


def delete_fdamage(name, username=""):
    """
    Delete fdamage
    """
    bucket="saferplaces.co"
    if username:
        key = f"fdamage/{username}/{juststem(name)}.csv"
        try:
            s3 = boto3.client('s3')
            s3.delete_object(Bucket=bucket, Key=key)
            return {
                "name": juststem(key),
                "value": key,
                "custom": ("shared/" not in key)
            }
        except Exception as e:
            return {
                "exception": f"{e}"
            }
    return {
        "exception": "username not provided"
    }

if __name__ == '__main__':
    
    arr = parse_fdamage(f_example)
    #upsert_user_fdamage("myfunc", arr, "valluzzi@gmail.com")
    #print("upsert_fdamage done")

    delete_fdamage("myfunc", "valluzzi@gmail.com")
    print("delete_fdamage done")
    


    arr = list_fdamages(prefix = "fdamage/valluzzi@gmail.com")
    for i in arr:
        print(i)

