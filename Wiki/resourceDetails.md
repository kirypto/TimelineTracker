# Resource Details

## Resources

The functionality provided by Timeline Tracker API supports 3 primary resources: Locations, Travelers, and Events.

__Locations__: Locations are places, cities, territories, biomes, counties, etc. Anything that has a defined area that a person or thing
could be 'inside' or
'outside' could be a Location.

__Travelers__: Travelers are people, animals, items of importance, and even ships or other moving craft. Travelers do not stay in one place,
moving from position to position.

__Events__: Events are the things that 'happen at' a Location or 'happen to' a Traveler. This could be a meeting between two people, a
natural disaster such as an earthquake, or the crowning of a queen. Events are what tie Locations and Travelers together.

The Timeline Tracker API is designed to help create, manage, and query these resources. The attributes of each differ slightly, but many
attributes are available for all of them such as tags for querying, metadata for any additional detail that may need, etc.

## Coordinates _(Dimensions)_

Timeline Tracker API is designed to provide a way of tracking the interactions between Locations and Travelers across time and space. In
order to facilitate the odd or bizarre movement that can occur in constructed worlds, the Timeline Tracker API is designed to support the 3
spacial dimensions as well as the 4th and 5th dimensions:

__Latitude__, __Longitude__, and __Altitude__: These are the 3 spacial dimensions. They can be used exactly as the similarly named
coordinate system of Earth, or they can be used arbitrarily as the 3 dimensions of a generally 2d environment such as that in DnD. In the
latter case, the specific name does not matter and would be the same as if the names were 'x', 'y', and 'z'. These 3 spacial dimension
coordinates can be any real number.

__Continuum__: Continuum is the 4th dimension _(time)_, named differently because continuum can be traveled either forward or backwards as
often happens in constructed worlds. Continuum coordinates can be any real number which allows any 'root' duration to be used. For example,
if a 'day' is the intended root duration, then 1.5 would be halfway through the second day.

__Reality__: Reality is the 5th and final supported dimension, which allows functionality of traveling back in continuum and speaking to
oneself or travelling to other realities entirely. Because something can either be in one reality or another _(there is no possibility of
being halfway between 2 distinct realities)_, reality coordinates must be integers.

For further details on the __Resources__ and __Coordinates__ outlined above, follow the link below to the more detailed Domain Design.

## Timelines

As the goal of Timeline Tracker API is to provide a way to get the entirety of a Location's or Traveler's history and interactions in the
'world', routes exist for these two resources' 'Timeline'.

__Location's Timeline__: The Timeline of a Location consists of the list of all events which affect the location, returned as a list of
identifiers ordered by the corresponding event's continuum. The list returned can be filtered to desired events using tags, etc.

__Traveler's Timeline__: The Timeline of a Traveler is similar to that of a location, but also includes the traveler's journey. This is
because _(unlike locations)_ travelers do not remain in one place throughout their existence, and could feasibly experience the same event
twice if the represented world allows for time travel. Thus, the returned timeline is the list of travel positions from the traveler's
journey interlaced with the identifiers of any events the traveler experienced along the way. Similar to with location timelines, the the
returned events can be filtered with tags, etc.
