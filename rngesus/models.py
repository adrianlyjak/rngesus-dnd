from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True)
    description = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default='active')

    characters = relationship("Character", back_populates="campaign")
    chats = relationship("Chat", back_populates="campaign")

class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    role = Column(String(100), nullable=False)
    type = Column(String(100), nullable=False)
    backstory = Column(Text, nullable=False)
    attributes = Column(String(255), nullable=False)
    primary_goal = Column(String(255), nullable=False)
    inventory = Column(String(255), nullable=False)

    campaign = relationship("Campaign", back_populates="characters")

class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    user_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)

    campaign = relationship("Campaign", back_populates="chats")