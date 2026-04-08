
# DASS Assignment 2 - Software Testing

## Repository

https://github.com/arpitmofficial/dass_assignment_2.git

## One-Drive Link

https://iiithydstudents-my.sharepoint.com/:u:/g/personal/arpit_mahtele_students_iiit_ac_in/IQAdcgUabFl0TorI1WtzzRcdAZole2EhJ0y-N1IJYt3HFXw?e=iO2NcQ

## How to Run the Code

### MoneyPoly (White Box)

From the repo root:

```bash
python whitebox/moneypoly/main.py
```

### StreetRace Manager (Integration)

This project is exercised through integration tests. Run tests below.

## How to Run the Tests

### White Box Tests

From the repo root:

```bash
python -m pytest whitebox/tests/ -v
```

### Integration Tests

From the repo root:

```bash
python -m pytest integration/tests/test_integration.py -v
```

### Black Box API Tests (QuickCart)

Start the API server, then run tests:

```bash
docker load -i blackbox/quickcart_image_x86.tar
docker run -d -p 8080:8080 --name quickcart quickcart

python -m pytest blackbox/tests/ -v
```
