import json
from flask import request, session, jsonify

from app.database.models import Category, Envelope
from app.database.database import db


def envelopes_edit_controller():

    # when user clicks on submit button on modal
    if request.method == 'PUT':
        env_id = request.form.get('edit_index')
        env_name = request.form.get('envelope_name_edit', '')
        env_description = request.form.get('envelope_description_edit')
        env_goal = int(request.form.get('envelope_goal_edit', 0))
        env_due_day = int(request.form.get('envelope_due_day_edit', 0))
        category_ids = request.form.get('modal_category[]') if request.form.get(
            'selected_categories') == '' else ','.join(set(request.form.get('selected_categories').split(',')))

        # name can't be empy
        if env_name == '':
            return jsonify({'valid': False, 'message': 'Nome não pode estar vazio'})

        # categories can't be empty
        if not category_ids or category_ids == '':
            return jsonify({'valid': False, 'message': 'Informar ao menos uma categoria'})

        # goal must be bigger then 0
        if not env_goal > 0:
            return jsonify({'valid': False, 'message': 'Meta deve ser maior que 0'})

        # due day must be between 1-31
        if not 0 < env_due_day <= 31:
            return jsonify({'valid': False, 'message': 'Dia de renovar envelope inválido'})

        old_envelope = db.session.query(Envelope).filter_by(id=env_id).first()

        # changing name...
        if old_envelope.env_name.upper() != env_name.upper():
            # can't have duplicate names
            envelope_same_name = db.session.query(
                Envelope
            ).filter(
                Envelope.user_id == old_envelope.user_id,
                Envelope.env_name == env_name,
            ).first()

            if len(envelope_same_name) > 0:
                return jsonify({'valid': False})

        if any([
            old_envelope.env_name != env_name,
            old_envelope.env_description != env_description,
            old_envelope.env_goal != env_goal,
            old_envelope.env_due_day != env_due_day,
            old_envelope.category_ids != category_ids
        ]):
            return jsonify({'valid': True})

        else:
            return jsonify({'valid': False})

    # when user clicks on edit button, to show information on modal
    user_id = session.get('user_id')
    envelope_id = request.form.get('detail')

    data_query = db.session.query(
        Envelope.id,
        Envelope.env_name,
        Envelope.env_description,
        Envelope.env_goal,
        Envelope.env_due_day,
        Envelope.category_ids
    ).filter(
        Envelope.id == envelope_id,
        Envelope.env_status == True,
        Envelope.user_id == user_id
    ).first()

    category_names = []
    for _id in list(filter(bool, data_query.category_ids.split(','))):
        category_names.append(Category.query.get(_id).cat_name)

    data = {
        'envelope':
            {
                'id': data_query.id,
                'name': data_query.env_name,
                'description': data_query.env_description,
                'goal': float(data_query.env_goal),
                'due_day': data_query.env_due_day,

                'category_names': category_names,
                'category_ids': list(filter(bool, data_query.category_ids.split(','))),
            }
    }

    return json.dumps(data)
