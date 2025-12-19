from sqlalchemy import Column, Integer, String, Float, Text, BigInteger, Date, DateTime
from app.db import Base

class Pharmacy(Base):
    __tablename__ = "pharmacy"
    
    # Using Korean column names as per schema
    ykiho = Column("암호화요양기호", String(255), primary_key=True)
    name = Column("약국명", String(255), nullable=False)
    address = Column("주소", String(500), nullable=True)
    tel = Column("전화번호", String(20), nullable=True)
    open_date = Column("개설일자", Date, nullable=True)
    x = Column("x", Float, nullable=True)
    y = Column("y", Float, nullable=True)

class SafePharmacy(Base):
    __tablename__ = "safe_pharmacy"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    tel = Column(String(50), nullable=True)
    x_coord = Column(Double if 'Double' in locals() else Float, nullable=True) # Schema says double. Float is fine in SA.
    y_coord = Column(Double if 'Double' in locals() else Float, nullable=True)
    license_date = Column(String(20), nullable=True)

class MasterMedical(Base):
    __tablename__ = "master_medical"
    
    care_id = Column(Text, primary_key=True) # Schema doesn't define PK explicitly but likely care_id or id. Using care_id as it looks unique.
    name = Column(Text)
    type_code = Column(BigInteger)
    type_name = Column(Text)
    sido = Column(Text)
    sigungu = Column(Text)
    town = Column(Text)
    address = Column(Text)
    zipcode = Column(BigInteger)
    tel = Column(Text)
    open_date = Column(DateTime)
    homepage = Column(Text)
    x = Column(Float)
    y = Column(Float)
    is_hospital = Column(BigInteger)
    departments = Column(Text)
    doctor_total = Column(BigInteger)
