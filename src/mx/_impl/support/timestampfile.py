#
# ----------------------------------------------------------------------------------------------------
#
# Copyright (c) 2024, 2024, Oracle and/or its affiliates. All rights reserved.
# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER.
#
# This code is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 only, as
# published by the Free Software Foundation.
#
# This code is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# version 2 for more details (a copy is included in the LICENSE file that
# accompanied this code).
#
# You should have received a copy of the GNU General Public License version
# 2 along with this work; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Please contact Oracle, 500 Oracle Parkway, Redwood Shores, CA 94065 USA
# or visit www.oracle.com if you need additional information or have any
# questions.
#
# ----------------------------------------------------------------------------------------------------
#

"""
Represents a file and its modification time stamp at the time the TimeStampFile is created.
"""
class TimeStampFile:
    def __init__(self, path, followSymlinks=True):
        """
        :type path: str
        :type followSymlinks: bool | str
        """
        assert isinstance(path, str), path + ' # type=' + str(type(path))
        self.path = path
        if exists(path):
            if followSymlinks == 'newest':
                self.timestamp = max(getmtime(path), lstat(path).st_mtime)
            elif followSymlinks:
                self.timestamp = getmtime(path)
            else:
                self.timestamp = lstat(path).st_mtime
        else:
            self.timestamp = None

    @staticmethod
    def newest(paths):
        """
        Creates a TimeStampFile for the file in `paths` with the most recent modification time.
        Entries in `paths` that do not correspond to an existing file are ignored.
        """
        ts = None
        for path in paths:
            if exists(path):
                if not ts:
                    ts = TimeStampFile(path)
                elif ts.isOlderThan(path):
                    ts = TimeStampFile(path)
        return ts

    def isOlderThan(self, arg):
        if not self.timestamp:
            return True
        if isinstance(arg, (int, float)):
            return self.timestamp < arg
        if isinstance(arg, TimeStampFile):
            if arg.timestamp is None:
                return False
            else:
                return arg.timestamp > self.timestamp
        if isinstance(arg, list):
            files = arg
        else:
            files = [arg]
        for f in files:
            if not os.path.exists(f):
                return True
            if getmtime(f) > self.timestamp:
                return True
        return False

    def isNewerThan(self, arg):
        """
        Returns True if self represents an existing file whose modification time
        is more recent than the modification time(s) represented by `arg`. If `arg`
        is a list, then it's treated as a list of path names.
        """
        if not self.timestamp:
            return False
        if isinstance(arg, (int, float)):
            return self.timestamp > arg
        if isinstance(arg, TimeStampFile):
            if arg.timestamp is None:
                return False
            else:
                return arg.timestamp < self.timestamp
        if isinstance(arg, list):
            files = arg
        else:
            files = [arg]
        for f in files:
            if self.timestamp < getmtime(f):
                return False
        return True

    def exists(self):
        return exists(self.path)

    def __str__(self):
        if self.timestamp:
            ts = time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(self.timestamp))
        else:
            ts = '[does not exist]'
        return self.path + ts

    def touch(self):
        if exists(self.path):
            os.utime(self.path, None)
        else:
            ensure_dir_exists(dirname(self.path))
            open(self.path, 'a')
        self.timestamp = getmtime(self.path)
