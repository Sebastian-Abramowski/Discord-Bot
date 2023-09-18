from marvel_character import MarvelCharacter


def test_update_with_found_result_not_successful():
    character = MarvelCharacter()
    assert not character.update_with_found_result({})


def test_update_with_found_result_successful():
    character = MarvelCharacter()
    result = {
        "name": "Hulk",
        "description": "Huge green strong",
        "thumbnail": {
            "path": "path_url_to_file",
            "extension": "png",
        },
        "comics": {
            "available": 1337
        }
    }
    assert character.update_with_found_result(result)
    assert character.name == "Hulk"
    assert character.description == "Huge green strong"
    assert character.image_url == "path_url_to_file.png"
    assert character.num_of_comics == 1337


def test_update_partly_matching_names():
    character = MarvelCharacter()
    assert character.update_partly_matching_names([])
    assert character.partly_maching_names == []


def test_update_partly_matching_names_with_results():
    character = MarvelCharacter()
    results = [
        {
            "name": "Hulk",
            "description": "Huge green strong",
            "thumbnail": {
                "path": "path_url_to_file",
                "extension": "png",
            },
            "comics": {
                "available": 1337
            }
        },
        {
            "name": "Hulk2",
            "description": "Huge green strong",
            "thumbnail": {
                "path": "path_url_to_file",
                "extension": "png",
            },
            "comics": {
                "available": 1337
            }
        },
    ]
    character.update_partly_matching_names(results)
    assert character.partly_maching_names == ["Hulk", "Hulk2"]
