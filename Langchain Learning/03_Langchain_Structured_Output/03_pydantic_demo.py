from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Student(BaseModel):
    name: str = "Shail"
    age: Optional[str] = None
    email: EmailStr
    cgpa: float = Field(gte=0, lte=10, default=5, description='Decimal value representing CGPA of the student')
    
new_student = {'email':"abc@gmail.com", 'cgpa':'10'}

student = Student(**new_student)

print(student)

student_dict = dict(student)
print(student_dict['age'])

student_json = student.model_dump_json()
