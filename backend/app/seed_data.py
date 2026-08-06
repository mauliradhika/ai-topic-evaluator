from .database import SessionLocal, engine, Base
from .models import Topic, Subtopic, Reference


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Topic).first():
        db.close()
        return  # already seeded

    data = {
        "Technology": [
            ("AI in Healthcare Diagnostics", "Discuss how AI models assist or replace diagnostic processes.",
             [("WHO report on AI in health (2021) discusses opportunities and risks of AI-assisted diagnostics.",
               "https://www.who.int/publications/i/item/9789240029200", "report")]),
            ("Data Privacy vs Personalization", "The tradeoff between personalized digital experiences and user data privacy.",
             [("GDPR Article 5 outlines core data processing principles including purpose limitation.",
               "https://gdpr-info.eu/art-5-gdpr/", "regulation")]),
        ],
        "Environment": [
            ("Carbon Capture Technology", "Viability and limitations of large-scale carbon capture.",
             [("IPCC Sixth Assessment Report discusses carbon dioxide removal methods and their scalability.",
               "https://www.ipcc.ch/report/ar6/wg3/", "report")]),
            ("Urban Green Spaces", "The role of green infrastructure in city planning.",
             [("UN-Habitat research links urban green space access to public health outcomes.",
               "https://unhabitat.org/", "report")]),
        ],
        "Economics": [
            ("Universal Basic Income", "Arguments for and against UBI as a policy tool.",
             [("Finland's 2017-2018 UBI trial results published by Kela (Finnish Social Insurance Institution).",
               "https://www.kela.fi/web/en/basic-income-experiment", "study")]),
            ("Gig Economy Labor Rights", "Employment classification debates in gig-based work.",
             [("ILO report on the gig economy addresses classification and labor protection gaps.",
               "https://www.ilo.org/", "report")]),
        ],
    }

    for topic_name, subtopics in data.items():
        topic = Topic(name=topic_name, category="general")
        db.add(topic)
        db.flush()
        for sub_name, desc, refs in subtopics:
            sub = Subtopic(topic_id=topic.id, name=sub_name, description=desc, difficulty="medium", weight=1.0)
            db.add(sub)
            db.flush()
            for citation, url, source_type in refs:
                db.add(Reference(subtopic_id=sub.id, citation_text=citation, url=url, source_type=source_type))

    db.commit()
    db.close()


if __name__ == "__main__":
    seed()
