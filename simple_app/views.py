from django.http import JsonResponse
import datetime
import json

from simple_app.models import Contact


def create_new_contact(payload: dict, link_precedence: str, linked_id: None = None) -> Contact:
    contact = Contact()
    contact.email = payload["email"]
    contact.phone_number = payload["phoneNumber"]
    contact.linked_id = linked_id
    contact.link_precedence = link_precedence
    contact.created_at = datetime.datetime.utcnow()
    contact.updated_at = datetime.datetime.utcnow()
    contact.save()
    return contact

# Create your views here.
def get_contact_data(request):
    if request.method != "POST":
        return JsonResponse({"message": "FAILED"})

    payload = json.loads(request.body.decode("utf-8"))
    datas = Contact.objects.filter(email=payload["email"]) | Contact.objects.filter(phone_number=payload["phoneNumber"])
    if len(datas) == 0:
        contact = create_new_contact(payload, "primary")
        contact_id = contact.id
        return JsonResponse(
            {
                "contact": {
                    "primaryContactId": contact_id,
                    "emails": [contact.email],
                    "phoneNumbers": [contact.phone_number],
                    "secondaryContactIds": [],
                }
            }
        )

    primary_datas = datas.filter(link_precedence="primary")
    if len(primary_datas) == 1:
        primary_data = primary_datas.get()
        secondary_datas = datas.filter(link_precedence="secondary")
        id_sets = set()
        for data in secondary_datas:
            id_sets.add(data.linked_id)
        if id_sets:
            matched_primary_datas = [Contact.objects.get(id=_id_) for _id_ in id_sets]
            matched_primary_datas.append(primary_data)
            matched_primary_datas = list(dict.fromkeys(matched_primary_datas))
            if len(matched_primary_datas) > 1:
                sorted_list = list(sorted(matched_primary_datas, key=lambda x: x.created_at))
                oldest_primary_data = sorted_list[0]
                matched_primary_datas = sorted_list[1:]
                for other_primary_data in matched_primary_datas:
                    other_primary_data.link_precedence = "secondary"
                    other_primary_data.linked_id = oldest_primary_data.id
                    other_primary_data.save()
                    all_related_secondary_datas = Contact.objects.filter(linked_id=other_primary_data.id)
                    for other_secondary_data in all_related_secondary_datas:
                        other_secondary_data.link_precedence = "secondary"
                        other_secondary_data.linked_id = oldest_primary_data.id
                        other_secondary_data.save()
                primary_data = oldest_primary_data
        all_secondary_datas = Contact.objects.filter(linked_id=primary_data.id)
        emails = [primary_data.email]
        phone_numbers = [primary_data.phone_number]
        secondary_contact_ids = []
        for secondary_data in all_secondary_datas:
            emails.append(secondary_data.email)
            emails = list(dict.fromkeys(emails))
            phone_numbers.append(secondary_data.phone_number)
            phone_numbers = list(dict.fromkeys(phone_numbers))
            secondary_contact_ids.append(secondary_data.id)
            secondary_contact_ids = list(dict.fromkeys(secondary_contact_ids))
        if any(payload[first] not in second for first, second in [("email", emails), ("phoneNumber", phone_numbers)]):
            new_contact = create_new_contact(payload, "secondary", primary_data.id)
            emails.append(new_contact.email)
            emails = list(dict.fromkeys(emails))
            phone_numbers.append(new_contact.phone_number)
            phone_numbers = list(dict.fromkeys(phone_numbers))
            secondary_contact_ids.append(new_contact.id)
            secondary_contact_ids = list(dict.fromkeys(secondary_contact_ids))
        return JsonResponse(
            {
                "contact": {
                    "primaryContactId": primary_data.id,
                    "emails": emails,
                    "phoneNumbers": phone_numbers,
                    "secondaryContactIds": secondary_contact_ids,
                }
            }
        )

    elif len(primary_datas) == 2:
        sorted_list = list(sorted(primary_datas, key=lambda x: x.created_at))
        primary_data_to_be_changed = sorted_list[1]
        oldest_primary_data = sorted_list[0]
        primary_data_to_be_changed.link_precedence = "secondary"
        primary_data_to_be_changed.linked_id = oldest_primary_data.id
        primary_data_to_be_changed.save()
        all_secondary_datas = Contact.objects.filter(linked_id=oldest_primary_data.id)
        emails = [oldest_primary_data.email]
        phone_numbers = [oldest_primary_data.phone_number]
        secondary_contact_ids = []
        for secondary_data in all_secondary_datas:
            emails.append(secondary_data.email)
            emails = list(dict.fromkeys(emails))
            phone_numbers.append(secondary_data.phone_number)
            phone_numbers = list(dict.fromkeys(phone_numbers))
            secondary_contact_ids.append(secondary_data.id)
            secondary_contact_ids = list(dict.fromkeys(secondary_contact_ids))
        return JsonResponse(
            {
                "contact": {
                    "primaryContactId": oldest_primary_data.id,
                    "emails": emails,
                    "phoneNumbers": phone_numbers,
                    "secondaryContactIds": secondary_contact_ids,
                }
            }
        )
    else:
        secondary_datas = datas.filter(link_precedence="secondary")
        id_sets = set()
        for data in secondary_datas:
            id_sets.add(data.linked_id)
        matched_primary_datas = [Contact.objects.get(id=_id_) for _id_ in id_sets]
        matched_primary_datas = list(dict.fromkeys(matched_primary_datas))
        sorted_list = list(sorted(matched_primary_datas, key=lambda x: x.created_at))
        oldest_primary_data = sorted_list[0]
        matched_primary_datas = sorted_list[1:]
        for other_primary_data in matched_primary_datas:
            other_primary_data.link_precedence = "secondary"
            other_primary_data.linked_id = oldest_primary_data.id
            other_primary_data.save()
            all_related_secondary_datas = Contact.objects.filter(linked_id=other_primary_data.id)
            for other_secondary_data in all_related_secondary_datas:
                other_secondary_data.link_precedence = "secondary"
                other_secondary_data.linked_id = oldest_primary_data.id
                other_secondary_data.save()
        primary_data = oldest_primary_data
        all_secondary_datas = Contact.objects.filter(linked_id=primary_data.id)
        emails = [primary_data.email]
        phone_numbers = [primary_data.phone_number]
        secondary_contact_ids = []
        for secondary_data in all_secondary_datas:
            emails.append(secondary_data.email)
            emails = list(dict.fromkeys(emails))
            phone_numbers.append(secondary_data.phone_number)
            phone_numbers = list(dict.fromkeys(phone_numbers))
            secondary_contact_ids.append(secondary_data.id)
            secondary_contact_ids = list(dict.fromkeys(secondary_contact_ids))
        if any(payload[first] not in second for first, second in [("email", emails), ("phoneNumber", phone_numbers)]):
            new_contact = create_new_contact(payload, "secondary", primary_data.id)
            emails.append(new_contact.email)
            emails = list(dict.fromkeys(emails))
            phone_numbers.append(new_contact.phone_number)
            phone_numbers = list(dict.fromkeys(phone_numbers))
            secondary_contact_ids.append(new_contact.id)
            secondary_contact_ids = list(dict.fromkeys(secondary_contact_ids))
        return JsonResponse(
            {
                "contact": {
                    "primaryContactId": primary_data.id,
                    "emails": emails,
                    "phoneNumbers": phone_numbers,
                    "secondaryContactIds": secondary_contact_ids,
                }
            }
        )


def fill_data(request):
    payload = json.loads(request.body.decode("utf-8"))
