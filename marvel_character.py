
class MarvelCharacter():
    def __init__(self):
        self.name = None
        self.description = None
        self.image_url = None
        self.num_of_comics = None
        self.num_of_matching_characters = None  # either 0 or 1 (limit=1)
        self.partly_maching_names = None

    def __str__(self):
        list_of_attributes = [self.name, self.description, self.image_url,
                              self.num_of_comics, self.num_of_matching_characters,
                              self.partly_maching_names]
        return "\n".join([str(attr) for attr in list_of_attributes])

    def try_updating_with_found_result(self, result: dict[str, object]) -> bool:
        # Returns True if it was successful, otherwise returns False
        try:
            char_name = result["name"]
            description = result["description"]
            image = ".".join([result["thumbnail"]["path"], result["thumbnail"]["extension"]])
            num_of_comics = result["comics"]["available"]

            self.name = char_name
            self.description = description
            self.image_url = image
            self.num_of_comics = num_of_comics
            return True
        except Exception as e:
            print(e)
            return False

    def try_updating_partly_matching_names(self, results: list[dict[str, object]]) -> bool:
        # Returns True if it was successful, otherwise returns False
        # This should be called when multiple results with matching character were found
        try:
            names = []
            for result_dict in results:
                names.append(result_dict["name"])
            self.partly_maching_names = names
            return True
        except Exception as e:
            print(e)
            return False
