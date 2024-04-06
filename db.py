# db.py
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    first_name = Column(String)
    last_name = Column(String)
    dob = Column(String)
    gender = Column(String)
    phone_number = Column(String)
    email = Column(String)
    user = relationship("User", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")

class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    visit_date = Column(Date)
    diagnosis = Column(Text)
    treatment = Column(Text)
    notes = Column(Text)
    patient = relationship("Patient", back_populates="medical_records")

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    appointment_date = Column(DateTime)
    purpose = Column(Text)
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    first_name = Column(String)
    last_name = Column(String)
    specialization = Column(String)
    contact_info = Column(String)
    user = relationship("User", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)
    logs = relationship("Log", back_populates="user", cascade="all, delete-orphan")
    doctor = relationship("Doctor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    patient = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    action = Column(String)
    timestamp = Column(DateTime)
    details = Column(Text)
    user = relationship("User", back_populates="logs")

# Створення бази даних
engine = create_engine('sqlite:///medical_management_system.db')
Base.metadata.create_all(engine)
