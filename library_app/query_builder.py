def query_builder(
    type: str | None = None,
    genre1: str | None = None,
    genre2: str | None = None,
    book_name: str | None = None,
    author: str | None = None,
    user_id: int | None = None,
):
    query = {}

    has_user_id = False
    if user_id:
        query['$and'] = [{'user_id': user_id}]
        has_user_id = True

    if genre1:
        genre_query = {'genre': genre1}

        if len(query) == 0:
            query[f'${type}'] = [genre_query]
        else:
            query['$and'].append({f'${type}': [genre_query]})

    if genre2:
        genre_query = {'genre': genre2}

        if len(query) == 0:
            query[f'${type}'] = [genre_query]
        elif len(query) == 1:
            if has_user_id:
                query['$and'].append({f'${type}': [genre_query]})
            else:
                query[f'${type}'].append(genre_query)
        else:
            query['$and'][1][f'${type}'].append(genre_query)

    if book_name:
        name_query = {'name': {'$regex': book_name}}

        if len(query) == 0:
            query[f'${type}'] = [name_query]
        elif len(query) == 1:
            if has_user_id:
                query['$and'].append({f'${type}': [name_query]})
            else:
                query[f'${type}'].append(name_query)
        else:
            query['$and'][1][f'${type}'].append(name_query)

    if author:
        author_query = {'author': {'$regex': author}}

        if len(query) == 0:
            query[f'${type}'] = [author_query]
        elif len(query) == 1:
            if has_user_id:
                query['$and'].append({f'${type}': [author_query]})
            else:
                query[f'${type}'].append(author_query)
        else:
            query['$and'][1][f'${type}'].append(author_query)

    return query
