from fastapi import Body, FastAPI,Response,HTTPException, status, Depends,APIRouter , Header
from sqlalchemy.orm import  Session
from typing import List, Optional
from sqlalchemy import func

from .. import schemas, models, oauth2

from .. database import get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(current_user: int = Depends(oauth2.get_current_user), db:Session = Depends(get_db),
 limit = 10, skip = 0, search:Optional[str] = ""):
    
    print(search)
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all() 
    # this will retrive the data with user id 
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote,
     models.Vote.post_id == models.Post.id , isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return results



@router.post("/",status_code=status.HTTP_201_CREATED, response_model= schemas.PostResponse)
def create_post(post:schemas.PostCreate, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute(""" insert into posts (title, content, published) values (%s,%s, %s) RETURNING * """,(post.title,post.content,post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    # print(current_user.email)
    # print(f"this is the user {current_user.id}")
    print(current_user.email)
    new_post = models.Post(**post.dict())
    new_post.owner_id = current_user.id
    
   

    db.add(new_post)
    db.commit() 
    db.refresh(new_post)

    return new_post


@router.get("/{id}",response_model=schemas.PostOut)
def get_post(id:int,db:Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user) ):
    # cursor.execute(""" select * from posts where id = %s""", (str(id)))
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote,
     models.Vote.post_id == models.Post.id , isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()


    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
                            
    return post



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db:Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user) ):
    # cursor.execute(""" delete from posts where id = %s returning * """, (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    deleted_post = post.first()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= f"post with id: {id} does not exist")
    
    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not Authorized to perform requested action")
     
    post.delete(synchronize_session=False)
    db.commit()
     
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}",response_model=schemas.PostResponse)
def update_post(id:int, updated_post:schemas.PostCreate,db:Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user) ):
    # cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s returning * """,(post.title, post.content,post.published,str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_to_update = db.query(models.Post).filter(models.Post.id == id).first()
    # updated_post = post.first()


    if post_to_update == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail= f"post with id: {id} does not exist")
    
    if post_to_update.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not Authorized to perform requested action")

    post_to_update.title = updated_post.title
    post_to_update.content = updated_post.content
    post_to_update.published = updated_post.published

    db.commit()
    return post_to_update.first()