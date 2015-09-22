# This file is part of Indico.
# Copyright (C) 2002 - 2015 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from flask import session

from indico.modules.events.registration.models.registrations import Registration
from indico.modules.events.registration.models.items import RegistrationFormSection
from indico.util.caching import memoize_request
from indico.web.forms.base import IndicoForm


def get_event_section_data(regform):
    sections = (RegistrationFormSection.find(registration_form=regform, is_deleted=False)
                                       .order_by(RegistrationFormSection.position))
    return [s.view_data for s in sections]


def make_registration_form(regform):
    """Creates a WTForm based on registration form fields"""

    form_class = type(b'RegistrationFormWTForm', (IndicoForm,), {})
    for form_item in regform.active_fields:
        field_impl = form_item.wtf_field
        if field_impl is None:
            continue
        name = 'field_{0}-{1}'.format(form_item.parent_id, form_item.id)
        setattr(form_class, name, field_impl.create_wtf_field())
    return form_class


def save_registration_to_session(registration):
    """Save a registration to the session"""
    session.setdefault('registrations', {})[registration.registration_form.id] = registration.id
    session.modified = True


@memoize_request
def was_regform_submitted(regform):
    """Check whether the current user has registered to a specific regform"""
    if session.user and session.user.registrations.filter_by(registration_form=regform).count():
        return True
    registration_id = session.get('registrations', {}).get(regform.id)
    if registration_id is None:
        return False
    return bool(Registration.find(id=registration_id).count())