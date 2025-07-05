from collections import UserDict
from functools import wraps

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)
    

class Name(Field):
    """
    Field Name for address book record
    """
    def __init__(self, value: str):
         super().__init__(str(value).strip().capitalize())

    def __eq__(self, value) -> bool:
         return str(self.value).lower() == str(value).strip().lower()


class PhoneFormatError(Exception):
     pass


def silent_phone_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PhoneFormatError:
            pass
    return wrapper


class Phone(Field):
    """
    Field Phone for address book record
    """
    def __init__(self, value: str):
        """
        International format phone number.
        Args:
            value (str): The phone number
        Raises:
            PhoneFormatError: when format of phone is wrong
        """
        phone = self._clear_phone(value)
        self._check_phone_format(phone)
        super().__init__(value)
    
    @staticmethod
    def _check_phone_format(phone):
        # TODO: can add other rules
        if not(8 <= len(phone) <= 15):
            raise PhoneFormatError("Wrong phone number format.")
    
    @staticmethod
    def _clear_phone(value) -> str:
        return "".join(ch for ch in str(value) if ch.isdigit())
         
    def __eq__(self, other) -> bool:
        if not isinstance(other, (Phone, str, int)):
            return NotImplemented
        if isinstance(other, Phone):
            return self.value == other.value
        try:
            return self.value == self._clear_phone(str(other))
        except:
            return False
    
    def __str__(self) -> str:
        return self.value  # TODO: can add number formating


class Record:
    """
    Record for address book.
    """
    def __init__(self, name: str):
        self.name: Name = Name(name)
        self._phones: list[Phone] = []  # TODO: move the phone logic to the PhoneList class

    @silent_phone_error
    def add_phone(self, phone: str) -> bool:
        phone_obj = Phone(phone)
        if phone_obj not in self._phones:
            self._phones.append(phone_obj)
            return True
        return False

    @silent_phone_error
    def delete_phone(self, phone: str) -> bool:
        phone_obj = Phone(phone)
        for p in self._phones:
            if p == phone_obj:
                self._phones.remove(p)
                return True
        return False
        
    @silent_phone_error
    def edit_phone(self, phone_old: str, phone_new: str) -> bool:
        phone_old_obj = Phone(phone_old)
        for i, p in enumerate(self._phones):
            if p == phone_old_obj:
                self._phones[i] = Phone(phone_new)
                return True
        return False
        
    @silent_phone_error
    def find_phone(self, phone: str):
        phone_obj = Phone(phone)
        return next((p for p in self._phones if p == phone_obj), None)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self._phones)}"


class AddressBook(UserDict[str, Record]):
    """
    Address book 
    """
    def add_record(self, record: Record):
        self.data[self._normalize_name(record.name)] = record

    def find(self, name: str) -> Record | None:
        return self.data.get(self._normalize_name(name))

    def delete(self, name: str):
        self.data.pop(self._normalize_name(name), None)

    def _normalize_name(self, name: str | Name) -> str:
        return str(name).strip().lower()

    def __getitem__(self, name: str) -> Record:
        return self.data[self._normalize_name(name)]
    
    def __setitem__(self, name: str, item: Record) -> None:
        self.data[self._normalize_name(name)] = item
