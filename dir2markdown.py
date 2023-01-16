import sys
import os
import sinode

here = os.path.dirname(os.path.abspath(__file__))

# an element within a chapter list is a paragraph
class Paragraph:
    def __init__(self, chapter, paragraph):
        self.chapter = chapter
        self.paragraph = paragraph

    def toMarkdown(self):
        self.outstring = ""
        # if this is a dictionary, it should be either graphed or listed
        if type(self.paragraph) == dict:
            if (
                "meta" in self.paragraph.keys()
                and self.paragraph["meta"]["type"] == "lineage"
            ):
                self.outstring += self.toGraph(
                    self.paragraph, name=self.paragraph["meta"]["name"]
                )

            else:
                self.outstring += self.listToMarkdown(self.paragraph)

        elif type(self.paragraph[0]) == list:
            self.outstring += self.listToMarkdown(self.paragraph[0])

        elif type(self.paragraph[0]) == str:
            for sentence in self.paragraph:
                if type(sentence) == str:
                    self.outstring += (
                        "<sup>" + str(self.chapter.verse) + "</sup> " + sentence + ". "
                    )
                    self.chapter.verse += 1
                else:
                    self.outstring += self.listToMarkdown(sentence)

        else:
            die
        return self.outstring

    def toGraphRecurse(self, content, parent=None):
        string = ""
        if type(content) == str:
            string += "'" + content + "' [shape=box]\n"
        elif type(content) == list:
            raise Exception("Lists not permitted")
        elif type(content) == dict:
            for k, v in content.items():
                print("Processing " + k)
                # dont record meta block
                if k == "meta":
                    continue

                # create this key
                keyWithQuotes = '"' + k + '"'
                print(keyWithQuotes)
                string += keyWithQuotes + " [shape=box, color = cadetblue1]\n"
                string += self.toGraphRecurse(v, parent=keyWithQuotes)
                # relationships
                if parent is not None:
                    string += parent + " -> " + keyWithQuotes + " [penwidth=1]\n"

        return string

    def toGraph(self, content, name):
        print("graphing")
        dotString = ""
        dotString += "digraph D {\n"
        dotString += self.toGraphRecurse(content)
        dotString += "}"

        filename = os.path.join("graphs", name.replace(" ", "_") + ".dot")
        with open(filename, "w+") as f:
            f.write(dotString)

        imagename = os.path.join("graphs", name.replace(" ", "_") + ".png")
        runstring = "dot -Tpng '" + filename + "' -o " + "'" + imagename + "'"
        print(runstring)
        os.system(runstring)

        retString = "\n![" + name + "](/" + imagename + '?raw=true "' + name + '")\n\n'

        return retString

    def listToMarkdown(self, content, depth=0):
        string = ""
        print(type(content))
        print(type(content) == str)
        if type(content) == str:
            string += "  " * depth
            string += "- "
            string += content + "\n"
        elif type(content) == list:
            for i in content:
                string += self.listToMarkdown(i, depth)
            # string += "\n"
        elif type(content) == dict:
            for k, v in content.items():
                if k == "meta":
                    continue
                string += "  " * depth
                string += "- "
                string += k
                string += "\n"
                string += self.listToMarkdown(v, depth + 1)
        elif content is None:
            pass
        else:
            print(type(content))
            die
        return string


# a file is equivalent to a chapter
class Chapter:
    def __init__(self, file, depth):
        print("Adding chapter " + file)
        self.depth = depth
        self.verse = 0
        self.paragraphs = []
        self.name = file.split(os.sep)[-1].replace(".py", "")
        with open(file, "r") as f:
            print(file)
            chapter = eval(f.read())
            for i, paragraph in enumerate(chapter):
                self.paragraphs += [Paragraph(chapter=self, paragraph=paragraph)]
        self.children = self.paragraphs

    def toMarkdown(self):

        # add its title
        self.outstring = "#" * (self.depth) + " " + self.name + "\n"

        for child in self.children:
            self.outstring += child.toMarkdown()
            # add a new line between paragraphs
            self.outstring += "\n\n"
        return self.outstring


class Category(sinode.Sinode):
    def __init__(self, directory, depth=0):
        sinode.Sinode.__init__(self)
        self.depth = depth
        self.chapters = []
        self.categories = []
        self.outstring = ""
        self.name = directory.split(os.sep)[-1]

        # read in ignore file
        if os.path.exists(os.path.join(directory, "ignore.py")):
            with open(os.path.join(directory, "ignore.py"), "r") as f:
                ignore = eval(f.read())
        else:
            ignore = []
        # print("Ignore " + str(ignore))

        # iterate over files
        for file in os.listdir(directory):
            if file in ignore or file == "ignore.py":
                continue
            resolved = os.path.join(directory, file)

            # if its a dir, its a subcategory
            if os.path.isdir(resolved):
                self.categories += [Category(resolved, depth + 1)]

            # otherwise, if it's a python file, execute it
            # each python file is a chapter, containing a list of paragraphs
            else:
                if file.endswith(".py"):
                    print("processing file " + file)
                    self.chapters += [Chapter(resolved, depth=depth + 1)]

    def toMarkdown(self):
        # add its title
        self.outstring += "#" * (self.depth) + " " + self.name + "\n"
        for chapter in self.chapters:
            self.outstring += chapter.toMarkdown()
        for category in self.categories:
            self.outstring += category.toMarkdown()
        return self.outstring


if __name__ == "__main__":
    m = Category(os.path.join(here, "Book Of Julian"), depth=1)

    preformat = m.toMarkdown()
    with open("README.md", "w+") as f:
        f.write(preformat)
    die
    preformat = preformat.replace("/graphs", os.path.join(here, "graphs"))
    preformat = preformat.replace("?raw=true", "")
    # preformat = preformat.replace("<sup>", "")
    # preformat = preformat.replace("</sup>", "")

    with open("README_formatted.md", "w+") as f:
        f.write(preformat)

    # os.system("mdpdf -o README.pdf README_formatted.md")
    os.system("pandoc --pdf-engine=xelatex README_formatted.md -s -o README.pdf")
