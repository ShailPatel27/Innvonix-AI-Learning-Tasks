# For Python:
# First, try to split along class definitions
# "\nclass ",
# "\ndef ",
# "\n\tdef ",
# Now split by the normal type of lines
# "\n\n",
# "\n",
# " ",
# "",

# Accepts these languages:
# CPP, GO, JAVA, KOTLIN, JS, TS, PHP, PROTO, PYTHON, R, RST, RUBY, RUST, SCALA, SWIFT, MARKDOWN, LATEX, HTML, SOL, CSHARP, COBOL, C, LUA, PERL, HASKELL, ELIXIR, POWERSHELL, VISUALBASIC6
# Each language has a different format to split

from langchain_text_splitters import RecursiveCharacterTextSplitter,Language

text = """
class Student:
    def __init__(self, name, age, grade):
        self.name = name
        self.age = age
        self.grade = grade  # Grade is a float (like 8.5 or 9.2)

    def get_details(self):
        return self.name"

    def is_passing(self):
        return self.grade >= 6.0


# Example usage
student1 = Student("Aarav", 20, 8.2)
print(student1.get_details())

if student1.is_passing():
    print("The student is passing.")
else:
    print("The student is not passing.")

"""

# Initialize the splitter
splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=300,
    chunk_overlap=0,
)

# Perform the split
chunks = splitter.split_text(text)

print(len(chunks))
print(chunks)