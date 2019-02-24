#coding: utf-8

class EditBuffer(object):
    #创建空文档，含有一个空行以及一个换行符，光标处于空行起始位置，插入模式
    def __init__(self):
        self._firstLine = _EditBufferNode(['\n'])
        self._lastLine = self._firstLine
        self._curLine = self._firstLine
        self._curlineNdx = 0
        self._curColNdx = 0
        self._numLines = 1
        self._insertMode = True

    #插入一个节点
    def _insertNode(self, _line, contents):
        new_Node = _EditBufferNode([])
        if self._lastLine == _line:
            _line.next = new_Node
            new_Node.prev = _line
            self._lastLine = new_Node
        else:
            _line.next.prev = new_Node
            new_Node.prev = _line
            new_Node.next = _line.next
            _line.next = new_Node.next
        new_Node.text.extend(contents)
        self._numLines += 1

    #删除一个节点
    def _removeNode(self, _line):
        if self._lastLine == _line:
            self._lastLine = _line.prev
            _line.prev.next = None
            _line.prev = None
        elif self._firstLine == _line:
            if self._firstLine == self._lastLine:
                _line.text.clear()
                _line.text.append('\n')
                return
            else:
                self._firstLine = _line.next
                _line.next.prev = None
                _line.next = None
        else:
            _line.prev.next = _line.next
            _line.next.prev = _line.prev
            _line.prev = None
            _line.next = None
        _line.text.clear()
        self._numLines -= 1
        del _line

    #返回总行数
    def numLines(self):
        return self._numLines

    #返回文本光标所在行的字符数
    def numChars(self):
        return len(self._curLine.text)

    #返回文本光标所在行的行号
    def lineIndex(self):
        return self._curlineNdx

    #返回文本光标所在列的列号
    def columnIndex(self):
        return self._curColNdx

    #设定输入模式，True是插入模式，False改写模式
    def setEntryMode(self, insert=True):
        self._insertMode = insert

    #切换输入模式
    def toggleEntryMode(self):
        self._insertMode = not self._insertMode

    #确定当前是否是插入模式
    def inInsertMode(self):
        return self._insertMode == True

    #返回文本光标所在位置的字符
    def getChar(self):
        return self._curLine.text[self._curColNdx]

    #返回光标所在行的所有内容,以字符串形式返回
    def getLine(self):
        lineStr = ''
        for ch in self._curLine.text:
            lineStr += ch
        return lineStr

    #光标竖直向上移动
    def moveUp(self, nlines):
        if nlines <= 0:
            return
        elif self._curlineNdx - nlines < 0:
            nlines = self._curlineNdx
        for i in range(nlines):
            self._curLine = self._curLine.prev
        self._curlineNdx -= nlines
        if self.numChars() < self._curColNdx:
            self._curColNdx = self.moveLineEnd()

    #光标向下移动
    def moveDown(self, nlines):
        if nlines <= 0:
            return
        elif self.numLines() - self.lineIndex() < nlines:
            nlines = self.numLines() - self.lineIndex()
        for i in range(nlines):
            self._curLine = self._curLine.next
        self._curlineNdx += nlines
        if self.numChars() < self._curColNdx:
            self.moveLineEnd()

    #光标移至文本开头
    def moveDocHome(self):
        self.moveUp(self.lineIndex())
        self.moveLineHome()

    #光标移动至文档结尾
    def moveDocEnd(self):
        self.moveDown(self.numLines() - self.lineIndex())
        self.moveLineEnd()

    def moveLeft(self):
        if self._curColNdx == 0:
            if self.lineIndex() > 0:
                self.moveUp(1)
                self.moveLineEnd()
        else:
            self._curColNdx -= 1

    def moveRight(self):
        if self._curColNdx == self.numChars():
            if self.lineIndex() < self.numLines() - 1:
                self.moveDown(1)
                self.moveLineHome()
        else:
            self._curColNdx += 1

    #光标移动到当前行开头
    def moveLineHome(self):
        self._curColNdx = 0
    def moveLineEnd(self):
        self._curColNdx = self.numChars() - 1

    #插入换行符时，另起一行，光标移动至该行起始位置
    def breakLine(self):
        nlContents = self._curLine.text[self._curColNdx:]
        del self._curLine.text[self._curColNdx:]
        self._curLine.text.append('\n')
        self._insertNode(self._curLine, nlContents)
        self._curlineNdx += 1
        self._curLine = self._curLine.next
        self._curColNdx = 0

    #删除光标所在行的内容，光标到下一行起始位置或上一行末尾
    def deleteLine(self):
        if self._curLine != self._lastLine:
            self._curLine = self._curLine.next
            self._curColNdx = 0
        else:
            self._curLine = self._curLine.prev
            self.moveLineEnd()
            self._curlineNdx -= 1
        self._removeNode(self._curLine)

    #删除光标到行末尾，不包含换行符
    def truncateLine(self):
        self._curLine.text = self._curLine.text[0:self.lineIndex()]

    #插入字符，考虑输入模式和插入字符是否是换行符
    def addChar(self, char):
        if char == '\n':
            self.breakLine()
        else:
            if self.inInsertMode():
                self._curLine.text.insert(self._curColNdx, char)
            else:
                if self.getChar() == '\n':
                    self._curLine.text.insert(self._curColNdx, char)
                else:
                    self._curLine.text[self._curColNdx] = char
            self._curColNdx += 1

    #删除字符
    def deleteChar(self):
        if self.getChar() != '\n':
            self._curLine.text.pop(self._curColNdx)
        else:
            if self._curLine == self._lastLine:
                return
            else:
                self._curLine.text.pop(self._curColNdx)
                self._curLine.text.extend(self._curLine.next.text)
                self._removeNode(self._curLine.next)

    #擦除字符，删除后光标向前移动一个字符，考虑换行符
    def ruboutChar(self):
        return
    #删除所有字符，仅保留一个空行和换行符
    def deleteAll(self):
        if self.numLines():
            self.deleteLine()

class _EditBufferNode(object):
    def __init__(self, text):
        self.text = text
        self.prev = None
        self.next = None



