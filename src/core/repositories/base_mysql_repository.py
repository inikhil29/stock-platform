from sqlalchemy.dialects.mysql import insert


class BaseMySQLRepository:

    def __init__(
        self,
        model,
        session_factory
    ):

        self.model = model

        self.session_factory = (
            session_factory
        )

    # ---------------------------------
    # INSERT ONE
    # ---------------------------------

    def insert_one(self, data):

        with self.session_factory() as session:

            obj = self.model(**data)

            session.add(obj)

            session.commit()

            session.refresh(obj)

            return obj

    # ---------------------------------
    # BULK INSERT
    # ---------------------------------

    def insert_many(self, records):

        if not records:
            return

        objects = [
            self.model(**record)
            for record in records
        ]

        with self.session_factory() as session:

            session.bulk_save_objects(
                objects
            )

            session.commit()

    # ---------------------------------
    # FIND BY ID
    # ---------------------------------

    def find_by_id(self, record_id):

        with self.session_factory() as session:

            return (
                session.query(self.model)
                .filter(
                    self.model.id == record_id
                )
                .first()
            )

    # ---------------------------------
    # FIND ONE
    # ---------------------------------

    def find_one(self, filters):

        with self.session_factory() as session:

            result = (
                session.query(self.model)
                .filter_by(**filters)
                .first()
            )

            return (
                result.to_dict()
                if result
                else None
            )

    # ---------------------------------
    # FIND MANY
    # ---------------------------------

    def find_many(
        self,
        filters=None,
        conditions=None,
        limit=100,
        offset=0
    ):

        with self.session_factory() as session:

            query = session.query(
                self.model
            )

            if filters:

                query = query.filter_by(
                    **filters
                )

            if conditions:

                query = query.filter(
                    *conditions
                )

            return (
                query
                .offset(offset)
                .limit(limit)
                .all()
            )

    # ---------------------------------
    # UPDATE
    # ---------------------------------

    def update_one(
        self,
        filters,
        update_data
    ):

        with self.session_factory() as session:

            count = (
                session.query(self.model)
                .filter_by(**filters)
                .update(update_data)
            )

            session.commit()

            return count

    # ---------------------------------
    # DELETE
    # ---------------------------------

    def delete_one(
        self,
        filters
    ):

        with self.session_factory() as session:

            count = (
                session.query(self.model)
                .filter_by(**filters)
                .delete()
            )

            session.commit()

            return count

    # ---------------------------------
    # BULK UPSERT
    # ---------------------------------

    def bulk_upsert(
        self,
        records,
        unique_columns=None
    ):

        if not records:
            return 0

        unique_columns = (
            unique_columns or []
        )

        stmt = insert(
            self.model
        ).values(records)

        update_dict = {

            c.name:
            stmt.inserted[c.name]

            for c in self.model.__table__.columns

            if c.name != "id"
            and c.name not in unique_columns
        }

        stmt = (
            stmt.on_duplicate_key_update(
                **update_dict
            )
        )

        with self.session_factory() as session:

            result = session.execute(
                stmt
            )

            session.commit()

            return result.rowcount
        
        
    # --------------------------------- 
    #  STREAM LARGE DATASETS 
    #  --------------------------------- 
    def stream( self, filters=None, conditions=None, batch_size=1000 ): 
        with self.session_factory() as session: 
            query = session.query( self.model ) 
            if filters: 
                query = query.filter_by( **filters ) 
            if conditions: 
                query = query.filter( *conditions ) 
            
            for row in query.yield_per( batch_size ): 
                yield row

    # ---------------------------------
    # UTILS
    # ---------------------------------

    def get_valid_columns(self):

        return {

            col.name

            for col
            in self.model.__table__.columns

            if col.name != "id"
        }