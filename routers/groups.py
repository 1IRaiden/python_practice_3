from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from database import db_manager as database_dependency
import crud
import schemas

router_group = APIRouter(prefix="/groups", tags=["Groups"])

@router_group.post("/", response_model=schemas.GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(group: schemas.GroupCreate, db: AsyncSession = Depends(database_dependency)):
    try:
        return await crud.create_group(db, group)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="""The group with such name already exists.
                    Please change name and retry again""")


@router_group.get("/", response_model=list[schemas.GroupRead])
async def get_all_groups(db: AsyncSession = Depends(database_dependency)):
    return await crud.get_all_groups(db)


@router_group.get("/{group_id}", response_model=schemas.GroupRead)
async def get_group(group_id: int, db: AsyncSession = Depends(database_dependency)):
    group = await crud.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return group


@router_group.delete("/{group_id}")
async def delete_group(group_id: int, db: AsyncSession = Depends(database_dependency)):
    success = await crud.delete_group(db, group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router_group.get("/{group_id}/students", response_model=list[schemas.StudentRead])
async def get_group_students(group_id: int, db: AsyncSession = Depends(database_dependency)):

    exists_group = await crud.group_exists(db, group_id)

    if not exists_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )

    students = await crud.get_students_by_group(db, group_id)
    return students

