#!/usr/bin/env python3
# encoding: utf-8
# ===============================================================================
#
#         FILE:  main.py
#
#        USAGE:  main.py [-t tag] [-g group]
#
#  DESCRIPTION:  This is a script that enhances ssh config, requires a specific format of ssh config
#
#      OPTIONS:  use_curses have bug, disable now
# REQUIREMENTS:  prettytable, please install prettytable before use, pip install prettytable
#         BUGS:  ---
#        NOTES:  ---
#       AUTHOR:  x2x4 (x2x4#x2x4.net)
#      COMPANY:  
#      VERSION:  3.3
#      CREATED:
#     REVISION:  ---
# ===============================================================================


import re
import sys
import os
import getopt
from typing import Tuple
from prettytable import PrettyTable
use_curses = False
import locale
try:
    import curses
    # use_curses = True
except ImportError:
    pass

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
code = locale.getpreferredencoding()

ssh_config = os.environ['HOME'] + '/.ssh/config'
re_search = {
    'host_tag': re.compile(r'^host\s*(.*)', re.IGNORECASE),
    'user': re.compile(r'^\s+user\s*(.*)', re.IGNORECASE),
    'hostname': re.compile(r'^\s+hostname\s*(.*)', re.IGNORECASE),
    'port': re.compile(r'^\s+port\s*(.*)', re.IGNORECASE),
    'group': re.compile(r'^#\s*group\s*(.*)', re.IGNORECASE),
    'tags': re.compile(r'^#\s*tags\s*(.*)', re.IGNORECASE)
}
server_list = []
argv_sort = 'hg:t:'
argv_long = ['help', 'group=', 'tags=']
running_options = {}
VERSION = '3.3'


def get_opts():
    try:
        opts, args = getopt.getopt(sys.argv[1:], argv_sort , argv_long)
        for opt,val in opts:
            if opt == '-g' or opt == '--group':
                running_options['group'] = val
            if opt == '-t' or opt == '--tags':
                running_options['tags'] = val
            if opt == '-h' or opt == '--help':
                usage()
    except getopt.GetoptError as e:
        running_options['group'] = 'ALL'
    if not 'tags' in running_options.keys():
        running_options['tags'] = 'NULL'
        if not 'group' in running_options.keys():
            running_options['group'] = 'ALL'
    else:
        if not 'group' in running_options.keys():
            running_options['group'] = 'NULL'
        elif running_options['group'] == 'ALL':
            running_options['group'] = 'NULL'


def usage(code=0):
    print("Usage:  %s [OPTIONS]" % sys.argv[0])
    print(" OPTIONS: ")
    print("  -g (value) | --group=(value)     List server with group")
    print("  -t (value) | --tags=(value)      List server with tags")
    print("  -h | --help                      This page")
    sys.exit(code)


def read_ssh_conf(config):
    global server_list
    conf = open(config)
    conf_file = conf.readlines()
    conf.close()
    now_num = 0
    first_time = 1
    for line in conf_file:
        line = line.rstrip()
        # 只能用rstrip，去除右边的回车符，如果用了strip会把前面的空格也去掉，导致re失败匹配
        for key in re_search.keys():
            # print(key)
            is_match = re_search[key].search(line)
            if is_match:
                #is_tag = cmp(key,'host_tag') # same as  if key == 'host_tag':
                is_tag = (key == 'host_tag')
                # print(is_match)
                # print(is_tag)
                match_str = is_match.groups()[0]
                # print(match_str)
                if is_tag == True:
                    if first_time == 1:
                        first_time = 0
                    else:
                        now_num += 1
                    
                    server_list.insert(now_num,{key : match_str})
                else:
                    server_list[now_num][key] = match_str
                #这里最终的数据结构为   server_list[0][key]=xxxx
    # debug
    # print(server_list)
    # remove global config
    # print(server_list)
    # set default
    for idx, server in enumerate(server_list):
        if 'hostname' not in server:
            server_list[idx]['hostname'] = None
        if 'port' not in server:
            server_list[idx]['port'] = "22"
    
    server_list = [ x for x in server_list if x['hostname'] is not None ]


def search_group(group,sort_id):
    # print 'group = ' + str(group);
    group_find = server_list[sort_id]['group'].find(str(group))
    if group_find >= 0:
        return True
    else:
        return False


def search_group_tags(group,tags,sort_id):
    # 2种情况，1) group == NULL 2) group 有值
    # print server_list[sort_id]
    is_find = 0
    if group == 'NULL':
        # only scan tags
        tags_find = server_list[sort_id]['tags'].find(str(tags))
        if tags_find >= 0:
            is_find = 1
    else:
        # scan group and tags
        group_find = server_list[sort_id]['group'].find(str(group))
        tags_find = server_list[sort_id]['tags'].find(str(tags))
        if group_find >=0 and tags_find >= 0 :
            is_find = 1
    if is_find > 0:
        return True
    else:
        return False


# v3 版本有3个条件，1) group 2) tags 3) group and tags
# group = ALL 忽略 tags值
# group 有值，tags为NULL
# group 有值，tags有值
def show_list_console(kuandu=108):
    print("SSH Manager (Version %s)" % VERSION)
    print('Group: %s \nTags: %s' % (running_options['group'], running_options['tags']))
    sort = 0
    show_id = []
    while sort < len(server_list):
        if not 'group' in server_list[sort]:
            server_list[sort]['group'] = 'UNDEFINED'
        if not 'tags' in server_list[sort]:
            server_list[sort]['tags'] = 'UNDEFINED'
        if running_options['group'] == 'ALL':
            # group = ALL
            show_id.append(sort)
        else:
            # 无tags
            if running_options['tags'] == 'NULL':
                if search_group(running_options['group'],sort):
                    show_id.append(sort)
            else:
                if search_group_tags(running_options['group'],running_options['tags'],sort):
                    show_id.append(sort)
        sort += 1
    if len(show_id) == 0:
        raise SystemExit('No server find')
    # print "=" * kuandu
    # print "| %-2s | %-30s | %-15s | %-15s | %30s |" % ('ID', 'Link Target', 'Group', 'Tags', 'Host Info')
    # print "-" * kuandu
    header = ['ID', 'Link Target', 'Group', 'Tags', 'Host Info']
    table = PrettyTable(header)
    for h in header:
        table.align[h] = 'l'
    table.align['Tags'] = 'r'
    for show_id_index,show_id_data in enumerate(show_id):
        # print "the length of (%s) is %d" %('Hello World',len('Hello World'))
        # print("| %-2d | %-30s | %-15s | %-15s | %30s |" % (show_id_index, server_list[show_id_data]['user']+'@'+server_list[show_id_data]['hostname']+':'+server_list[show_id_data]['port'], server_list[show_id_data]['group'], server_list[show_id_data]['tags'],  server_list[show_id_data]['host_tag']))
        table.add_row([
            show_id_index,
            server_list[show_id_data]['user']+'@'+server_list[show_id_data]['hostname']+':'+server_list[show_id_data]['port'],
            server_list[show_id_data]['group'],
            server_list[show_id_data]['tags'],
            server_list[show_id_data]['host_tag']
            ]) 
    # print "-" * kuandu
    # return show_id
    print(table)
    return show_id


def show_list_curses() -> Tuple[str, str, str, str]:
    user: str
    host_target: str
    host_port: str
    host_tag: str
    input_num: int
    sort = 0
    show_id = []
    get_input = None
    while sort < len(server_list):
        if 'group' not in server_list[sort]:
            server_list[sort]['group'] = 'UNDEFINED'
        if 'tags' not in server_list[sort]:
            server_list[sort]['tags'] = 'UNDEFINED'
        if running_options['group'] == 'ALL':
            # group = ALL
            show_id.append(sort)
        else:
            # 无tags
            if running_options['tags'] == 'NULL':
                if search_group(running_options['group'],sort):
                    show_id.append(sort)
            else:
                if search_group_tags(running_options['group'],running_options['tags'],sort):
                    show_id.append(sort)
        sort += 1

    if len(show_id) == 0:
        raise SystemExit('No server find')
    try:
        loop = True
        while loop:
            screen = curses.initscr()
            curses.echo()
            height, width = screen.getmaxyx()
            # 设置颜色
            curses.start_color()
            # 绿底黑字
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
            # 白底蓝字
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
            # 黑底什么字
            curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            line_last = height - 3
            screen.clear()
            screen.border(0)
            # screen.addstr(1, 1, "SSH Manager (Version %s)" % VERSION, curses.color_pair(1))
            screen.addstr(1, 1, "SSH Manager (Version %s)" % VERSION)
            # screen.addstr(2, 1, "  Group: %s" % running_options['group'], curses.color_pair(1))
            screen.addstr(2, 1, "  Group: %s" % running_options['group'])
            # screen.addstr(3, 1, "  Tags: %s" % running_options['tags'], curses.color_pair(1))
            screen.addstr(3, 1, "  Tags: %s" % running_options['tags'])
            screen.refresh()
            screen.hline(4, 1, curses.ACS_HLINE,width-2)
            screen.addstr(5,3, "%-2s | %-30s | %-15s | %-30s | %s " % ('ID', 'Link Target', 'Group', 'Tags', 'Host Info'))#,curses.color_pair(1))
            screen.hline(6, 1, curses.ACS_HLINE,width-2)
            next_line = 7
            # 数据要分段了
            for show_id_index, show_id_data in enumerate(show_id):
                screen.addstr(next_line, 3, "%-2d | %-30s | %-15s | %-30s | %s" % (show_id_index, server_list[show_id_data]['user']+'@'+server_list[show_id_data]['hostname']+':'+server_list[show_id_data]['port'], server_list[show_id_data]['group'], server_list[show_id_data]['tags'],  server_list[show_id_data]['host_tag']))
                # screen.hline(next_line+1, 1, curses.ACS_HLINE,width-2)
                next_line = next_line + 1
            screen.addstr(height-2, 1, "Page |  %-8s  |  %-8s  |  %-8s  |" % ('n(Next)', 'p(Previous)', 'x(Exit)'))
            screen.hline(height-3, 1, curses.ACS_HLINE,width-2)
            screen.addstr(height-4, 1, "Please input the ID: ")

            get_input = screen.getstr(height-4, 22, 60)
            screen.refresh()
            # raise RuntimeError(str(get_input))
            if b"x" == get_input:
                raise KeyboardInterrupt
            try:
                input_num = int(get_input)
                # if input_num < l
                loop = False
            except (TypeError, ValueError):
                # print("\nType or ValueError error")
                pass

    except KeyboardInterrupt:
        curses.endwin()
        print("\nBye...")
        sys.exit(0)
    finally:
        curses.endwin()
    # return get_input
    user = server_list[show_id[input_num]]['user']
    host_target = server_list[show_id[input_num]]['hostname']
    host_port = server_list[show_id[input_num]]['port']
    host_tag = server_list[show_id[input_num]]['host_tag']
    return user, host_target, host_port, host_tag


def show_list_nocurses() -> Tuple[str, str, str, str]:
    user: str
    host_target: str
    host_port: str
    host_tag: str
    try:
        forever = True
        while forever:
            show_id = show_list_console()
            input_num = input('Input [ID] number: ')
            if input_num.isdigit():
                for index_id, s_id in enumerate(show_id):
                    input_num = int(input_num)
                    if input_num == index_id:
                        forever = False
                        break
                if forever:
                    print("Wrong Input. Again !!\n")
            else:
                print("Wrong Input. Again !!\n")
    except KeyboardInterrupt as e:
        print("\nBye...")
        sys.exit(0)
    user = server_list[show_id[input_num]]['user']
    host_target = server_list[show_id[input_num]]['hostname']
    host_port = server_list[show_id[input_num]]['port']
    host_tag = server_list[show_id[input_num]]['host_tag']
    return user, host_target, host_port, host_tag


def run():
    input_num = -1
    user: str
    host_target: str
    host_port: str
    host_tag: str
    if use_curses:
        user, host_target, host_port, host_tag = show_list_curses()
    else:
        # try:
        #     forever = True
        #     while forever:
        #         show_id = show_list_console()
        #         input_num = input('Input [ID] number: ')
        #         if input_num.isdigit():
        #             for index_id, s_id in enumerate(show_id):
        #                 input_num = int(input_num)
        #                 if input_num == index_id:
        #                     forever = False
        #                     break
        #             if forever:
        #                 print("Wrong Input. Again !!\n")
        #         else:
        #             print("Wrong Input. Again !!\n")
        # except KeyboardInterrupt as e:
        #     print("\nBye...")
        #     sys.exit(0)
        # user = server_list[show_id[input_num]]['user']
        # host_target = server_list[show_id[input_num]]['hostname']
        # host_port = server_list[show_id[input_num]]['port']
        # host_tag = server_list[show_id[input_num]]['host_tag']
        user, host_target, host_port, host_tag = show_list_nocurses()
    # print(type(input_num))
    try:
        to_number = int(input_num)
    except (TypeError, ValueError):
        print("\nType or ValueError error")
        sys.exit(1)

    if input_num >= to_number:
        print("[INFO] Connect to %s@%s:%s !!" % (user, host_target, host_port))
        print(os.execl('/usr/bin/env', 'this_not_use', 'ssh', host_tag))
    

def main():
    get_opts()
    read_ssh_conf(ssh_config)
    run()
    # show_list_curses()


if __name__ == '__main__':
    main()
