import logging
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings
from backend.utils.security import hash_password

logger = logging.getLogger(__name__)

# Setup MongoDB client
client = AsyncIOMotorClient(settings.MONGO_URI)
# Motor client allows getting default database from connection string, fallback to "portfolio"
db = client.get_database("portfolio")

# Collection helpers
admin_collection = db["admin"]
profile_collection = db["profile"]
skills_collection = db["skills"]
projects_collection = db["projects"]
education_collection = db["education"]
certifications_collection = db["certifications"]
experience_collection = db["experience"]
messages_collection = db["messages"]
custom_sections_collection = db["custom_sections"]

def serialize_doc(doc) -> dict:
    if not doc:
        return None
    return {
        "id": str(doc["_id"]),
        **{k: v for k, v in doc.items() if k != "_id"}
    }

def serialize_list(docs) -> list:
    return [serialize_doc(doc) for doc in docs]

async def init_db():
    logger.info("--- STARTING DATABASE INITIALIZATION ---")
    # 1. Admin Seeding (Using clashing-safe portfolio settings)
    try:
        logger.info(f"Targeting database name: {db.name}")
        admin_count = await admin_collection.count_documents({})
        logger.info(f"Current admin count in collection '{admin_collection.name}': {admin_count}")
        if admin_count == 0:
            username = settings.PORTFOLIO_ADMIN_USERNAME
            password = settings.PORTFOLIO_ADMIN_PASSWORD
            logger.info(f"Seeding admin user with username: '{username}'")
            if not password:
                logger.error("PORTFOLIO_ADMIN_PASSWORD is empty or None!")
                raise ValueError("PORTFOLIO_ADMIN_PASSWORD cannot be empty")
            
            hashed_pwd = hash_password(password)
            await admin_collection.insert_one({
                "username": username,
                "password": hashed_pwd
            })
            logger.info(f"Database seeded successfully: Admin user '{username}' created.")
        else:
            logger.info("Admin user already exists, skipping seeding.")
    except Exception as e:
        logger.error(f"CRITICAL ERROR during admin seeding: {e}", exc_info=True)

    # 2. Profile Seeding
    try:
        profile_count = await profile_collection.count_documents({})
        if profile_count == 0:
            default_profile = {
                "name": "Jane Doe",
                "title": "Full Stack Developer",
                "taglines": [
                    "Building high-performance web applications.",
                    "Passionate about clean code and modern design.",
                    "FastAPI & React developer."
                ],
                "profile_image": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=400&h=400",
                "resume_url": "https://example.com/resume.pdf",
                "social_links": {
                    "github": "https://github.com",
                    "linkedin": "https://linkedin.com",
                    "twitter": "https://twitter.com",
                    "email": "jane.doe@example.com",
                    "instagram": "https://instagram.com"
                },
                "availability_status": "Available for Freelance & Full-time",
                "about_bio": "I am a dedicated full-stack developer with experience in python, react, and cloud technologies. I love building tools that solve real-world problems and creating interfaces that are a joy to use.",
                "about_title": "Crafting digital experiences with precision & code",
                "footer_text": "Jane Doe. All rights reserved.",
                "section_visibility": {
                    "hero": True,
                    "about": True,
                    "skills": True,
                    "projects": True,
                    "education": True,
                    "certifications": True,
                    "experience": True,
                    "contact": True
                }
            }
            await profile_collection.insert_one(default_profile)
            logger.info("Database seeded: Default profile information created.")
    except Exception as e:
        logger.error(f"Error seeding default profile: {e}")

    logger.info("Database connection and initialization checked successfully.")