def get_context(chat_session):

    context = chat_session.context

    if not isinstance(context, dict):
        context = {}

    return context


def update_context(
    chat_session,
    **values
):

    context = get_context(
        chat_session
    )

    context.update(values)

    chat_session.context = context

    chat_session.save(
        update_fields=[
            "context",
            "updated_at",
        ]
    )

    return context


def clear_context(chat_session):

    chat_session.context = {}

    chat_session.save(
        update_fields=[
            "context",
            "updated_at",
        ]
    )