from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.task_schema import CreateTask, DeleteTask, UpdateTask, TaskBase
from models.user_model import User
from models.task_model import Task
from database import get_db
from dependencies import get_token
from jose import JWTError

router = APIRouter(
    prefix='/tasks',
    tags=['tasks'],
    dependencies=[Depends(get_token)]
)


@router.get('/')
def all_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_token)):

    tasks = db.query(Task).filter(
        current_user['author_id'] == Task.author_id,Task.status==1).all()
    return {'tasks': [
        {
            'tasks_id': task.task_id,
            'author_id': task.author_id,
            'task_name': task.task_name,
            'created_at': task.created_at,
            'updated_at': task.updated_at
        }
        for task in tasks
    ]
    }


@router.get('/done')
def done_task(db: Session = Depends(get_db), current_user: User = Depends(get_token)):

    tasks = db.query(Task).filter(
        current_user['author_id'] == Task.author_id, Task.task_is_complete == 1,Task.status==1).all()
    return {'tasks': [
        {
            'tasks_id': task.task_id,
            'author_id': task.author_id,
            'task_name': task.task_name,
            'created_at': task.created_at,
            'updated_at': task.updated_at
        }
        for task in tasks
    ]
    }


@router.post('/')
def create(task: CreateTask, db: Session = Depends(get_db), current_user: User = Depends(get_token)):
    try:
        author_id = current_user['author_id']
        new_task = Task(
            author_id=author_id,
            task_name=task.task_name
        )
        db.add(new_task)
        db.commit()
        return {'message': 'Task created successfully!'}
    except JWTError:
        raise HTTPException(status_code=400, detail='Invalid JWT token')


@router.put('/')
def update_task(taskReq: UpdateTask, db: Session = Depends(get_db), current_user: User = Depends(get_token)):

    if not db.query(Task).filter(Task.task_id == taskReq.task_id, current_user['author_id'] == Task.author_id).update({
        'task_name': taskReq.task_name,
        'task_is_complete': taskReq.task_is_complete
    }):
        raise HTTPException(404, 'Task not found. Failed to update.')
    db.commit()
    return {
        'message': 'Task updated successfully!',
    }


@router.delete('/')
def delete_task(taskReq: TaskBase, db: Session = Depends(get_db), current_user: User = Depends(get_token)):

    if not db.query(Task).filter(Task.task_name == taskReq.task_name,
                                 current_user['author_id'] == Task.author_id).delete():
        raise HTTPException(404, 'Task not found. Deletion failed.')
    db.commit()
    return {'message': 'Task deleted successfully!', }

@router.put('/delete')
def softdel(task: DeleteTask, db: Session = Depends(get_db), current_user: User = Depends(get_token)):

    if not db.query(Task).filter(Task.task_id == task.task_id, current_user['author_id'] == Task.author_id).update({
        'status':task.status
    }):
        raise HTTPException(404, 'Task not found. Failed to delete.')
    db.commit()
    return {'message': 'Task deleted successfully.'}