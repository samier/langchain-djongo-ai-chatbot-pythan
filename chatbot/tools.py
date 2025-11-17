"""
Tools and Functions for LangChain Agent to call external APIs.
"""
import requests
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class StudentData(BaseModel):
    """Schema for student creation data."""
    student_name: str = Field(description="Full name of the student")
    student_id: str = Field(description="Unique student ID (5 digits)")
    grade: str = Field(description="Student's grade/class (e.g., Grade 10)")
    email: str = Field(description="Student's contact email")
    phone: Optional[str] = Field(None, description="Student's phone number (optional)")
    address: Optional[str] = Field(None, description="Student's address (optional)")


@tool
def create_student_api(
    student_name: str,
    student_id: str,
    grade: str,
    email: str,
    phone: str = "",
    address: str = ""
) -> str:
    """
    Call the external API to create a new student.
    
    Args:
        student_name: Full name of the student
        student_id: Unique student ID (must be 5 digits)
        grade: Student's grade/class
        email: Student's email address
        phone: Student's phone number (optional)
        address: Student's address (optional)
    
    Returns:
        Success or error message from the API
    """
    # Validation
    if not student_id.isdigit() or len(student_id) != 5:
        return f"Error: Student ID must be exactly 5 digits. Got: {student_id}"
    
    if "@" not in email:
        return f"Error: Invalid email format: {email}"
    
    # Prepare API payload
    payload = {
        "name": student_name,
        "student_id": student_id,
        "grade": grade,
        "email": email,
    }
    
    if phone:
        payload["phone"] = phone
    if address:
        payload["address"] = address
    
    # TODO: Replace with your actual API endpoint
    api_endpoint = "http://your-api-endpoint.com/api/students"
    
    try:
        # Uncomment when you have actual API
        # response = requests.post(api_endpoint, json=payload, timeout=10)
        # response.raise_for_status()
        # result = response.json()
        
        # Mock response for now
        result = {
            "success": True,
            "student_id": student_id,
            "name": student_name,
            "message": "Student created successfully"
        }
        
        if result.get("success"):
            return f"✅ Student created successfully!\nStudent ID: {student_id}\nName: {student_name}\nGrade: {grade}\nEmail: {email}"
        else:
            return f"❌ Error creating student: {result.get('error', 'Unknown error')}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ API Error: Unable to reach student creation service. {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def validate_student_data(
    student_name: str = "",
    student_id: str = "",
    grade: str = "",
    email: str = ""
) -> str:
    """
    Validate student data against documentation requirements.
    
    Args:
        student_name: Student's full name
        student_id: Student ID to validate
        grade: Student's grade
        email: Student's email
    
    Returns:
        Validation result with any errors found
    """
    errors = []
    warnings = []
    
    # Validate student name
    if student_name:
        if len(student_name) < 2:
            errors.append("Student name must be at least 2 characters")
        if not all(c.isalpha() or c.isspace() for c in student_name):
            warnings.append("Student name should only contain letters")
    
    # Validate student ID
    if student_id:
        if not student_id.isdigit():
            errors.append("Student ID must contain only numbers")
        elif len(student_id) != 5:
            errors.append(f"Student ID must be exactly 5 digits (got {len(student_id)})")
    
    # Validate grade
    if grade:
        valid_grades = ["Grade 9", "Grade 10", "Grade 11", "Grade 12", "KG", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6", "Grade 7", "Grade 8"]
        if grade not in valid_grades:
            errors.append(f"Invalid grade. Must be one of: {', '.join(valid_grades)}")
    
    # Validate email
    if email:
        if "@" not in email or "." not in email.split("@")[1]:
            errors.append("Invalid email format")
    
    # Build response
    if errors:
        return "❌ Validation failed:\n" + "\n".join(f"- {error}" for error in errors)
    elif warnings:
        return "⚠️ Validation passed with warnings:\n" + "\n".join(f"- {warning}" for warning in warnings)
    else:
        return "✅ All provided data is valid"


@tool
def get_student_requirements() -> str:
    """
    Get the required fields for creating a student from documentation.
    
    Returns:
        List of required fields and their validation rules
    """
    return """
📋 Student Creation Requirements (from documentation):

Required Fields:
1. Student Name: Full name (minimum 2 characters, letters only)
2. Student ID: Unique 5-digit number (e.g., 12345)
3. Grade/Class: One of [KG, Grade 1-12]
4. Email: Valid email address

Optional Fields:
5. Phone: Contact phone number
6. Address: Student's address

Validation Rules:
- Student ID must be unique (5 digits, numeric only)
- Email must be in valid format (contains @ and domain)
- Grade must match ClassCare standards
- Name should contain only letters and spaces
"""


# List of all available tools
AVAILABLE_TOOLS = [
    create_student_api,
    validate_student_data,
    get_student_requirements,
]


def get_tools() -> List:
    """Return list of available tools for the agent."""
    return AVAILABLE_TOOLS

