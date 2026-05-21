from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from database import db_manager as database_dependency
import crud, schemas


router_student = APIRouter(prefix="/students", tags=["Students"])

@router_student.post("/", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
async def create_student(student: schemas.StudentCreate, db: AsyncSession = Depends(database_dependency)):
    try:
        return await crud.create_student(db, student)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Count not create the student with such params. Please check params of student"
        )


@router_student.get("/", response_model=list[schemas.StudentRead])
async def get_all_students(db: AsyncSession = Depends(database_dependency)):
    return await crud.get_all_students(db)

@router_student.get("/{student_id}", response_model=schemas.StudentRead)
async def get_student(student_id: int, db: AsyncSession = Depends(database_dependency)):
    student = await crud.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router_student.delete("/{student_id}")
async def delete_student(student_id: int, db: AsyncSession = Depends(database_dependency)):
    success = await crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router_student.post("/{student_id}/group/{group_id}")
async def add_to_group(student_id: int, group_id: int, db: AsyncSession = Depends(database_dependency)):
    success = await crud.add_student_to_group(db, student_id, group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student or group not found")
    return success

@router_student.delete("/{student_id}/group/")
async def remove_from_group(student_id: int, db: AsyncSession = Depends(database_dependency)):
    success = await crud.remove_student_from_group(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router_student.put("/{student_id}/transfer/{new_group_id}")
async def transfer_student(student_id: int, new_group_id: int, db: AsyncSession = Depends(database_dependency)):
    success = await crud.move_student_to_group(db, student_id, new_group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student or group not found")

    return success
