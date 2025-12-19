
from sqlalchemy.orm import Session
from app.models.user import UserProfile 
from app.schemas.user import UserProfileUpdate, UserProfileResponse, FamilyMemberRequest, UserRegisterRequest 
from app.security.password_handler import get_password_hash 


# =======================================================
# 1. 로그인한 주 사용자 프로필 조회
# =======================================================
def get_user_profile(db: Session, user_id: int):
    """ PK id를 기준으로 조회합니다. """
    return db.query(UserProfile).filter(UserProfile.id == user_id).first()


# =======================================================
# 2. 가족 구성원 목록 조회
# =======================================================
def get_family_members(db: Session, owner_id: int):
    """ user_id가 owner_id인 모든 레코드를 조회합니다. (본인은 제외) """
    # owner_id를 참조하면서 본인 ID와 다른 레코드를 찾습니다.
    return db.query(UserProfile).filter(UserProfile.user_id == owner_id, UserProfile.id != owner_id).all()


# =======================================================
# 3. 프로필 상세 정보 수정 (마이페이지 핵심)
# =======================================================
def update_user_profile_detail(db: Session, user_id: int, update_data: UserProfileUpdate) -> UserProfile:
    """ 특정 ID의 사용자가 자신의 상세 프로필 정보를 수정합니다. """
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()

    if not user:
        # 이 함수는 인증된 사용자에게만 호출되므로, 발생 확률은 낮습니다.
        raise ValueError("사용자 프로필을 찾을 수 없습니다.")

    # exclude_unset=True: Pydantic 객체에서 값이 설정되지 않은 필드는 제외
    update_dict = update_data.model_dump(exclude_unset=True) 

    # 1. 비밀번호 해시 처리
    if 'pw' in update_dict and update_dict['pw']:
        # 🚨 get_password_hash 함수가 비밀번호를 해시한다고 가정
        update_dict['pw'] = get_password_hash(update_dict['pw'])

    # 2. 프로필 정보 업데이트
    for key, value in update_dict.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


# =======================================================
# 4. 사용자 회원가입 (신규 추가)
# =======================================================
def register_user(db: Session, user_data: UserRegisterRequest) -> UserProfile:
    """ 신규 사용자를 등록합니다. """
    # 1. 이메일 중복 확인
    existing_user = db.query(UserProfile).filter(UserProfile.email == user_data.email).first()
    if existing_user:
        raise ValueError("이미 등록된 이메일입니다.")

    # 2. 비밀번호 해시
    hashed_pw = get_password_hash(user_data.password)

    # 3. DB 모델 생성
    new_user = UserProfile(
        email=user_data.email,
        hashed_password=hashed_pw,
        name=user_data.name,
        phone_num=user_data.phone_num,
        age=user_data.age
    )

    db.add(new_user)
    db.flush() # ID 생성을 위해 flush
    
    # 4. 기본 환자 프로필(본인) 생성
    from app.models.user import PatientProfile
    default_patient = PatientProfile(
        user_id=new_user.id,
        name=new_user.name,
        relation="Self",
        birth_date=None, # 입력받으면 좋음
        gender=None
    )
    db.add(default_patient)

    db.commit()
    db.refresh(new_user)
    
    return new_user