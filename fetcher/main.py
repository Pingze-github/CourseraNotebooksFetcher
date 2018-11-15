
# Download coursera notebooks, like https://hub.coursera-notebooks.org/user/jzpvoopfcbteoxgjrpwsyv/tree

import os
import re
from urllib.parse import quote
import json
import base64

from gevent import monkey
monkey.patch_all()
import requests

from XGreenletPool import XGreenletPool, XTask, Queue

tree_save_dir = 'tree_save'

def escape_path(path):
    return re.sub('\\|/|:|\*|\?|<|>|\|', '', path)

def get_repoKey(rootUrl):
    """
    Get the key pattern for the notebooks repository
    :param rootUrl:
    :return:
    """
    matches = re.search('/user/(\w+)/tree', rootUrl)
    return matches.group(1)

def create_prefix(repoKey):
    """
    create the url prefix for all need to be download
    :param repoKey:
    :return:
    """
    return 'https://hub.coursera-notebooks.org/user/{}/api/contents'.format(repoKey)

def get_path_res(prefix, path, timeout=30):
    path = quote(path)
    url = prefix + '/' + path
    print('fetching url:', url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        'Cookie': cookie,
    }
    return requests.get(url, headers=headers, timeout=timeout)

def get_path_data(prefix, path):
    print('Got directory:', path)
    r = get_path_res(prefix, path)
    return json.loads(r.text)

def get_path_file_content(prefix, path):
    print('Fetching file content of', path)
    r = get_path_res(prefix, path, timeout=300)
    print('Fetched file content of', path)

    try:
        data = json.loads(r.text)
    except Exception:
        raise Exception('Got content not json, maybe the cookie expired')

    content = data['content']
    if data['format'] == 'base64':
        content = base64.b64decode(content)
    elif data['format'] == 'json':
        content = json.dumps(content, indent=1)
    return content


def getTree(prefix, startPath='/'):
    data = get_path_data(prefix, startPath)
    for sub in data['content']:
        path = sub['path']
        if sub['type'] == 'directory':
            sub['content'] = getTree(prefix, path)['content']
    return data

def saveTree(tree, repoKey):
    mkdirs_no_error(tree_save_dir)
    savepath = tree_save_dir + '/tree_' + repoKey + '.json'
    with open(savepath, 'w') as f:
        f.write(json.dumps(tree, indent=1))
    print('Tree {} saved!'.format(repoKey))
    return savepath

def loasTree(savepath):
    with open(savepath, 'r') as f:
        tree = json.loads(f.read())
    return tree

def mkdirs_no_error(path):
    path = escape_path(path)
    try:
        os.makedirs(path)
    except Exception as e:
        # ignore error "the file already exists"
        if e.errno != 17:
            raise e

def downFile(prefix, path, rootDir):
    content = get_path_file_content(prefix, path)
    path = escape_path(path)
    localPath = rootDir + '/' + path
    flag = 'w'
    if type(content) == bytes:
        flag = 'wb'
    with open(localPath, flag) as f:
        f.write(content)

def createLocalRepo(prefix, node, rootDir):
    path = node['path'] or ''
    mkdirs_no_error(rootDir + '/' + path)
    for sub in node['content']:
        if sub['type'] == 'directory':
            createLocalRepo(prefix, sub, rootDir)
        else:
            # downFile(prefix, sub['path'], rootDir)
            queue_download.put(XTask(downFile, [prefix, sub['path'], rootDir]))
            # downFile(prefix, sub['path'], rootDir)


def main():
    global cookie
    cookie = 'jupyter-hub-token-jzpvoopfcbteoxgjrpwsyv="2|1:0|10:1542243920|40:jupyter-hub-token-jzpvoopfcbteoxgjrpwsyv|44:ZjM2MjRiYzcyMTkyNDAyMWEwZTMyMzA5OGM3MTllYTc=|be46f1a7a8b80e800bd7ec5fd934f037f52a1526d356a725f35472c993ea0856"; _xsrf=2|8448f35f|939cb795c6d4b6440e3dd0d269470845|1541988505; AWSALB=M7tXhmyKF4IdPJ/Ze304Oj+UxiXR9oZsMtp5bWcL2NbM7iuT1Re8gWTXhsadZZ77GDH+1EBrTB66tcuAF56+QWtST6pMHemfPDa7K8EMvNFbyvWmMzq0ZFMJcP8c'

    # ### YOUR CODE START ###
    # The web page of the notebooks repository's root path
    rootUrl = 'https://hub.coursera-notebooks.org/user/jzpvoopfcbteoxgjrpwsyv/tree'
    # ### YOUR CODE END ###

    # create key data
    repoKey = get_repoKey(rootUrl)
    prefix = create_prefix(repoKey)
    print('Parsed repo key:', repoKey)

    # fetch file tree to local path
    tree = getTree(prefix)
    savepath = saveTree(tree, repoKey)

    # download task put into queue
    global queue_download
    queue_download = Queue.Queue()

    # download files & create directories with the tree data
    # savepath = 'tree_jzpvoopfcbteoxgjrpwsyv.json'
    tree = loasTree(savepath)
    createLocalRepo(prefix, tree, 'repo/NerualNetwork')

    # async download with size
    pool = XGreenletPool(queue_download, size=3)
    pool.run()


if __name__ == '__main__':
    main()

