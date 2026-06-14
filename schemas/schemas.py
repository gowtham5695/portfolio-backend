from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# ----------------- AUTHENTICATION SCHEMAS -----------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AdminLogin(BaseModel):
    username: str
    password: str

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

# ----------------- PROFILE & HERO SCHEMAS -----------------
class SocialLinks(BaseModel):
    github: str = ""
    linkedin: str = ""
    twitter: str = ""
    email: str = ""
    instagram: str = ""

class SectionVisibility(BaseModel):
    hero: bool = True
    about: bool = True
    skills: bool = True
    projects: bool = True
    education: bool = True
    certifications: bool = True
    experience: bool = True
    contact: bool = True

class ProfileUpdate(BaseModel):
    name: str
    title: str
    taglines: List[str] = Field(default_factory=list)
    profile_image: str = ""
    resume_url: str = ""
    social_links: SocialLinks = Field(default_factory=SocialLinks)
    availability_status: str = "Available for work"
    about_bio: str = ""
    about_title: str = ""
    about_card_title: str = "Constant Learning"
    about_card_desc: str = "I'm continuously refining my knowledge of algorithms, systems architecture, and UI/UX design trends to deliver top-notch products."
    footer_text: str = ""
    section_visibility: SectionVisibility = Field(default_factory=SectionVisibility)

class ProfileResponse(ProfileUpdate):
    id: str

# ----------------- SKILL SCHEMAS -----------------
class SkillCreate(BaseModel):
    name: str
    category: str  # e.g., Frontend, Backend, Database, Mobile, etc.
    level: int = Field(default=100, ge=0, le=100)
    icon: str = "Code"  # Lucide icon name

class SkillResponse(SkillCreate):
    id: str

# ----------------- PROJECT SCHEMAS -----------------
class ProjectCreate(BaseModel):
    title: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    image: str = ""  # URL to image
    github_link: str = ""
    live_link: str = ""

class ProjectResponse(ProjectCreate):
    id: str

# ----------------- EDUCATION SCHEMAS -----------------
class EducationCreate(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    duration: str  # e.g., "2020 - 2024"
    description: str = ""
    grade: str = ""

class EducationResponse(EducationCreate):
    id: str

# ----------------- CERTIFICATION SCHEMAS -----------------
class CertificationCreate(BaseModel):
    title: str
    issuer: str
    date: str  # e.g., "June 2026"
    verification_link: str = ""

class CertificationResponse(CertificationCreate):
    id: str

# ----------------- EXPERIENCE SCHEMAS -----------------
class ExperienceCreate(BaseModel):
    company: str
    role: str
    duration: str  # e.g., "Jan 2025 - Present"
    description: str
    certificate_link: str = ""

class ExperienceResponse(ExperienceCreate):
    id: str

# ----------------- MESSAGE SCHEMAS -----------------
class MessageCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str = "Portfolio Contact"
    message: str

class MessageResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    subject: str
    message: str
    created_at: datetime

# ----------------- CUSTOM SECTION SCHEMAS -----------------
class CustomSectionCreate(BaseModel):
    title: str
    subtitle: str = ""
    content: str
    order: int = 0
    visible: bool = True

class CustomSectionResponse(CustomSectionCreate):
    id: str
