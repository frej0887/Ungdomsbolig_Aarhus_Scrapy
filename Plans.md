
#My plans

## Maps services

### APIs
* Google Maps Distance Matrix API
* OpenStreetMap API

### How to integrate it
* Choose a location and get every apartment in a specific distance (only if it is for free) 
* Distance from specific locations

### Locations for Maps
(Evt. som færre)

* Ny Munkegade
* Health
* Nobelparken

Andre
* Katrinebjerg
* BSS
* VIA Viby
* Nørreport/Kystvejen

Evt.
* Dalgas Ave.
* Moesgaard
* Aarhus H

##Website
* Django
* Floor plan icon as a tiny grey and white simple floor plan


##Sort
* Rent
* Area
* Distance from location

##Filter
| Filter name | How to sort | Which fields | 
| :---------- | :---------- | :----------- |
| Rent | max | integer |
| Down payment | max | integer | 
| Area | choose | checkbox |
| Wait | min | dropdown |
| Facilities | choose own | checkbox |
| Room count | minimum | float | 
| Distance | max | float, a unit(dropdown) and a transit type(dropdown) | 
