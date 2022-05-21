# Some of the variables in this file likely shouldn't be hard coded
# and should moved into the config file
# such as:
#  temp for heat exhaustion warning

class SafetyTopics:

   def __init__(self, document):

      # contains strings with individual safety topic information for day
      # if no safety topics for the day, the list will be empty
      self.topics: list[Str] = list()      

      # the document which the safety topics will be added to
      # this is included so weather and tide information can be accessed 
      self.doc = document
      self._fill()

   def _fill(self):
      '''
      generate all relevant safety topic strings for the day and append
      them to the topics list
      '''
      self.heat_exhaustion()
      self.tide_too_low_for_woods()

   def heat_exhaustion(self):

      if self.doc.weather and \
                  any(hour.temp >= 30 for hour in self.doc.weather):
         pt1 = 'Watch out for Heat Exhaustion. Alternate staff working' 
         pt2 = ' in the sun, drink plenty of water'
         self.topics.append(pt1 + pt2)

   def tide_too_low_for_woods(self):
      woods_inaccessible = [tide for tide in self.doc.tides['hourly'] if \
                 tide.is_too_low_for_woods()]
      if any(tide.is_within_operational_hours() \
                 for tide in woods_inaccessible):
         start = woods_inaccessible[0].time.strftime('%-I %p')
         end = woods_inaccessible[-1].time.strftime('%-I %p')
         pt1 = 'Tides too low to access channel behind Woods Island'
         pt2 = f' from {start} to {end}'
         self.topics.append(pt1 + pt2)
