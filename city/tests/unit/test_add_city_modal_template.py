# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

import pytest
from bs4 import BeautifulSoup
from bs4.element import AttributeValueList, Tag
from django.template.loader import render_to_string


def class_names(tag: Tag) -> set[str]:
    classes = tag.get('class')
    if isinstance(classes, AttributeValueList):
        return set(classes)
    if isinstance(classes, str):
        return {classes}
    return set()


@pytest.mark.unit
def test_add_city_modal_souvenir_toggle_stays_inside_modal() -> None:
    html = render_to_string('components/add-city-modal.html')
    soup = BeautifulSoup(html, 'html.parser')

    checkbox = soup.find('input', {'id': 'magnet-checkbox'})
    assert isinstance(checkbox, Tag)

    wrapper = checkbox.find_parent(class_='cursor-pointer')
    assert isinstance(wrapper, Tag)
    wrapper_classes = class_names(wrapper)
    text_block = wrapper.find('div')

    assert 'dui-label' not in wrapper_classes
    assert 'grid' not in wrapper_classes
    assert {'flex', 'w-full', 'items-center', 'gap-4'}.issubset(wrapper_classes)
    assert isinstance(text_block, Tag)
    assert {'min-w-0', 'flex-1'}.issubset(class_names(text_block))
    assert 'shrink-0' in class_names(checkbox)


@pytest.mark.unit
def test_add_city_modal_form_text_has_readable_contrast() -> None:
    html = render_to_string('components/add-city-modal.html')
    soup = BeautifulSoup(html, 'html.parser')

    label_texts = soup.select('#form-add-city .dui-label-text')
    helper_texts = soup.select('#form-add-city span.block.text-sm, #form-add-city textarea')

    assert label_texts
    assert helper_texts

    for label_text in label_texts:
        classes = class_names(label_text)
        assert 'text-secondary' not in classes
        assert 'text-base-content' in classes

    for helper_text in helper_texts:
        classes = class_names(helper_text)
        assert 'opacity-70' not in classes
        if helper_text.name != 'textarea':
            assert 'text-base-content/80' in classes


@pytest.mark.unit
def test_add_city_modal_field_titles_have_space_before_content() -> None:
    html = render_to_string('components/add-city-modal.html')
    soup = BeautifulSoup(html, 'html.parser')

    field_labels = soup.select('#form-add-city .dui-form-control > label.dui-label')

    assert field_labels
    for field_label in field_labels:
        assert 'mb-2' in class_names(field_label)


@pytest.mark.unit
def test_add_city_modal_uses_neutral_controls_and_joined_date_shortcuts() -> None:
    html = render_to_string('components/add-city-modal.html')
    soup = BeautifulSoup(html, 'html.parser')

    modal_title = soup.find('h3', {'id': 'addCityModalLabel'})
    assert isinstance(modal_title, Tag)
    assert 'text-base-content' in class_names(modal_title)
    assert 'text-primary' not in class_names(modal_title)

    form_controls = soup.select(
        '#form-add-city select, #form-add-city #add-city-city, '
        '#form-add-city #date-of-visit, #form-add-city #impression'
    )
    assert form_controls
    for control in form_controls:
        assert 'dui-select-primary' not in class_names(control)
        assert 'dui-input-primary' not in class_names(control)
        assert 'dui-textarea-primary' not in class_names(control)

    date_input = soup.find('input', {'id': 'date-of-visit'})
    today_button = soup.find('button', {'id': 'today-button'})
    yesterday_button = soup.find('button', {'id': 'yesterday-button'})

    assert isinstance(date_input, Tag)
    assert isinstance(today_button, Tag)
    assert isinstance(yesterday_button, Tag)

    date_join = date_input.find_parent(class_='dui-join')
    assert isinstance(date_join, Tag)
    assert date_join is today_button.find_parent(class_='dui-join')
    assert date_join is yesterday_button.find_parent(class_='dui-join')

    for control in (date_input, today_button, yesterday_button):
        classes = class_names(control)
        assert 'dui-join-item' in classes
        assert 'dui-btn-primary' not in classes
        assert 'dui-btn-accent' not in classes


@pytest.mark.unit
def test_add_city_modal_rating_stars_use_gold_warning_color() -> None:
    html = render_to_string('components/add-city-modal.html')
    soup = BeautifulSoup(html, 'html.parser')

    rating_stars = soup.select('#rating-container input[type="radio"]')

    assert len(rating_stars) == 5
    for star in rating_stars:
        classes = class_names(star)
        assert 'dui-bg-warning' not in classes
        assert 'bg-warning' in classes
