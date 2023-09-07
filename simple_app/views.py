from django.http import JsonResponse
import datetime
import json

from simple_app.models import Contact


def create_new_contact(payload: dict,
                       link_precedence: str,
                       linked_id: None = None) -> Contact:
    contact = Contact()
    contact.email = payload["email"]
    contact.phone_number = payload["phoneNumber"]
    contact.linked_id = linked_id
    contact.link_precedence = link_precedence
    contact.created_at = datetime.datetime.utcnow()
    contact.updated_at = datetime.datetime.utcnow()
    contact.save()
    return contact


def get_all_primary_contact_ids(datas) -> set:
    secondary_datas = datas.filter(link_precedence="secondary")
    id_sets = set()
    for data in secondary_datas:
        id_sets.add(data.linked_id)
    return id_sets


def sort_by_oldest_contact(datas: list) -> list:
    sorted_list = list(sorted(datas, key=lambda x: x.created_at))
    return sorted_list


def seperate_oldest_from_contacts(datas: list) -> tuple:
    oldest_primary_data = datas[0]
    other_primary_datas = datas[1:]
    return oldest_primary_data, other_primary_datas


def make_primary_contacts_secondary(other_primary_datas: list, oldest_primary_data):
    for other_primary_data in other_primary_datas:
        other_primary_data.link_precedence = "secondary"
        other_primary_data.linked_id = oldest_primary_data.id
        other_primary_data.save()
        all_related_secondary_datas = Contact.objects.filter(linked_id=other_primary_data.id)
        if len(all_related_secondary_datas) == 0:
            return
        make_primary_contacts_secondary(all_related_secondary_datas, oldest_primary_data)


def add_to_list_without_duplicates(entity_to_add, list_to_be_added_to):
    if entity_to_add not in list_to_be_added_to:
        list_to_be_added_to.append(entity_to_add)
    return list_to_be_added_to


def get_related_secondary_contact_details(primary_data):
    emails = [primary_data.email]
    phone_numbers = [primary_data.phone_number]
    secondary_contact_ids = []
    all_secondary_datas = Contact.objects.filter(linked_id=primary_data.id)
    for secondary_data in all_secondary_datas:
        emails = add_to_list_without_duplicates(secondary_data.email, emails)
        phone_numbers = add_to_list_without_duplicates(secondary_data.phone_number, phone_numbers)
        secondary_contact_ids = add_to_list_without_duplicates(secondary_data.id, secondary_contact_ids)
    return emails, phone_numbers, secondary_contact_ids


# Create your views here.
def get_contact_data(request):
    if request.method != "POST":
        return JsonResponse({"status": "FAILED",
                             "message": "ONLY POST REQUEST IS ALLOWED"})

    payload = json.loads(request.body.decode("utf-8"))
    datas = Contact.objects.filter(email=payload["email"]) | Contact.objects.filter(phone_number=payload["phoneNumber"])

    if len(datas) == 0: # No matches for request
        contact = create_new_contact(payload, "primary")
        return JsonResponse(
            {
                "contact": {
                    "primaryContactId": contact.id,
                    "emails": [contact.email],
                    "phoneNumbers": [contact.phone_number],
                    "secondaryContactIds": [],
                }
            }
        )

    primary_datas = datas.filter(link_precedence="primary")
    if len(primary_datas) == 1: # Only one primary contact is matched for the request
        primary_data = primary_datas.get() # Get the primary contact
        id_sets = get_all_primary_contact_ids(datas)
        if id_sets:
            id_sets.add(primary_data.id) # Remove duplicates for available primary contact ids
            matched_primary_datas = [Contact.objects.get(id=_id_) for _id_ in id_sets]
            if len(matched_primary_datas) > 1:
                sorted_list = sort_by_oldest_contact(matched_primary_datas)
                oldest_primary_data, other_primary_datas = seperate_oldest_from_contacts(sorted_list)
                make_primary_contacts_secondary(other_primary_datas, oldest_primary_data)
                primary_data = oldest_primary_data
        emails, phone_numbers, secondary_contact_ids = get_related_secondary_contact_details(primary_data)
        if any(payload[first] not in second for first, second in [("email", emails), ("phoneNumber", phone_numbers)]):
            # Creation of new secondary contact if new information is available
            new_contact = create_new_contact(payload, "secondary", primary_data.id)
            emails = add_to_list_without_duplicates(new_contact.email, emails)
            phone_numbers = add_to_list_without_duplicates(new_contact.phone_number, phone_numbers)
            secondary_contact_ids = add_to_list_without_duplicates(new_contact.id, secondary_contact_ids)
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

    elif len(primary_datas) == 2: # Multiple primary contact is matched
        sorted_list = sort_by_oldest_contact(primary_datas)
        oldest_primary_data, other_primary_datas = seperate_oldest_from_contacts(sorted_list)
        make_primary_contacts_secondary(other_primary_datas, oldest_primary_data)
        emails, phone_numbers, secondary_contact_ids = get_related_secondary_contact_details(oldest_primary_data)
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
        id_sets = get_all_primary_contact_ids(datas)
        matched_primary_datas = [Contact.objects.get(id=_id_) for _id_ in id_sets]
        sorted_list = sort_by_oldest_contact(matched_primary_datas)
        oldest_primary_data, other_primary_datas = seperate_oldest_from_contacts(sorted_list)
        make_primary_contacts_secondary(other_primary_datas, oldest_primary_data)
        primary_data = oldest_primary_data
        emails, phone_numbers, secondary_contact_ids = get_related_secondary_contact_details(primary_data)
        if any(payload[first] not in second for first, second in [("email", emails), ("phoneNumber", phone_numbers)]):
            # Creation of new secondary contact if new information is available
            new_contact = create_new_contact(payload, "secondary", primary_data.id)
            emails = add_to_list_without_duplicates(new_contact.email, emails)
            phone_numbers = add_to_list_without_duplicates(new_contact.phone_number, phone_numbers)
            secondary_contact_ids = add_to_list_without_duplicates(new_contact.id, secondary_contact_ids)
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

