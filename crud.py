from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from models import Student, Group
from schemas import StudentCreate, GroupCreate

from sqlalchemy import delete, select, update


async def create_student(db: AsyncSession, student_data: StudentCreate):
    # check group_id exist such group or not
    target_group_id = student_data.group_id

    # if group not exist then we indicate that group is none
    if target_group_id is not None:
        result = await db.execute(select(Group).where(Group.id == target_group_id))
        group = result.scalars().first()

        if not group:
            target_group_id = None


    # create student
    db_student = Student(
        first_name=student_data.first_name,
        last_name=student_data.last_name,
        age=student_data.age,
        group_id=target_group_id
    )

    db.add(db_student)

    # save changes and update
    await db.commit()
    await db.refresh(db_student)

    # update amount in group
    if target_group_id is not None:
        await increment_members_count(db, target_group_id)

    return db_student

async def create_group(db: AsyncSession, group_data: GroupCreate):
    db_group = Group(name=group_data.name)
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group

async def get_student_by_id(db: AsyncSession, student_id: int):
    result = await db.execute(select(Student).where(Student.id == student_id))
    return result.scalars().first()

async def delete_student(db: AsyncSession, student_id: int):
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)

    # check group and do decrement
    student = result.scalars().first()
    if not student:
        return False

    if student.group_id is not None:
        await decrement_members_count(db, student.group_id)

    await db.execute(delete(Student).where(Student.id == student_id))
    await db.commit()

    return True

async def get_group_by_id(db: AsyncSession, group_id: int):
    result = await db.execute(select(Group).where(Group.id == group_id))
    return result.scalars().first()

async def delete_group(db: AsyncSession, group_id: int):
    await db.execute(
        update(Student)
        .where(Student.group_id == group_id)
        .values(group_id=None)
    )

    result = await db.execute(delete(Group).where(Group.id == group_id))
    await db.commit()

    return result.rowcount > 0

# can add limit for constraint
async def get_all_students(db: AsyncSession):
    result = await db.execute(select(Student))
    return result.scalars().all()

# can add limit for constraint
async def get_all_groups(db: AsyncSession):
    result = await db.execute(select(Group))
    return result.scalars().all()


async def add_student_to_group(db: AsyncSession, student_id: int, group_id: int):
    # find student
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalars().first()

    if not student:
        return False

    old_group_id = student.group_id

    if old_group_id == group_id:
        return True

    if old_group_id is not None:
        await decrement_members_count(db, old_group_id)

    if group_id is not None:
        await increment_members_count(db, group_id)

    await db.execute(
        update(Student)
        .where(Student.id == student_id)
        .values(group_id=group_id)
    )

    await db.commit()
    return True

# guess that student can have only one group
async def remove_student_from_group(db: AsyncSession, student_id: int):
    stmt = update(Student).where(Student.id == student_id).values(group_id=None)
    result = await db.execute(stmt)

    student = result.scalars().first()

    if not student:
        return False

    if student.group_id is not None:
        await decrement_members_count(db, student.group_id)

    await db.execute(
        update(Student)
        .where(Student.id == student_id)
        .values(group_id=None)
    )

    await db.commit()

    return result


async def get_students_by_group(db: AsyncSession, group_id: int):
    result = await db.execute(select(Student).where(Student.group_id == group_id))
    return result.scalars().all()

async def move_student_to_group(db: AsyncSession, student_id: int, new_group_id: int):
    # Does student exist
    result_student = await db.execute(select(Student).where(Student.id == student_id))
    student = result_student.scalars().first()

    if not student:
        return None

    # Does group exist
    group_exist = await db.execute(select(Group).where(Group.id == new_group_id))

    if not group_exist.scalars().first():
        return None

    old_group_id = student.group_id

    if old_group_id == new_group_id:
        return student

    # update old group
    if old_group_id is not None:
        await decrement_members_count(db, old_group_id)

    # update new group
    await increment_members_count(db, new_group_id)

    stmt = update(Student).where(Student.id == student_id).values(group_id=new_group_id)
    result = await db.execute(stmt)

    await db.commit()
    await db.refresh(student)

    return result


async def group_exists(db: AsyncSession, group_id: int) -> bool:
    # check exist group or not, if group not exists we will send error
    result = await db.execute(select(Group).where(Group.id == group_id))
    return result.scalars().first() is not None


async def increment_members_count(db: AsyncSession, group_id: int):
    await db.execute(
        update(Group)
        .where(Group.id == group_id)
        .values(members_count=Group.members_count + 1)
    )
    await db.commit()

async def decrement_members_count(db: AsyncSession, group_id: int):
    await db.execute(
        update(Group)
        .where(Group.id == group_id)
        .values(members_count=Group.members_count - 1)
    )
    await db.commit()
