def generate_pagination_list(
        objs,
        instance_generator: callable,
        page: int,
        limit: int = 20
) -> dict:
    total_count = objs.count()
    instance_list = [instance_generator(obj) for obj in objs.paginate(page=page, paginate_by=limit)]
    return {
        "total_count": total_count,
        "list": instance_list,
    }


def generate_all_list(
        objs,
        instance_generator: callable
) -> dict:
    total_count: int = objs.count()
    instance_list = [instance_generator(obj) for obj in objs]
    return {
        "total_count": total_count,
        "list": instance_list,
    }
