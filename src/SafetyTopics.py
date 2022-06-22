# Some of the variables in this file likely shouldn't be hard coded
# and should moved into the config file
# such as:
#  temp for heat exhaustion warning
from time import strftime
from Weather import Weather

class SafetyTopics:

   def __init__(self, document):

      # contains strings with individual safety topic information for day
      # if no safety topics for the day, the list will be empty
      self.topics: list[str] = list()      

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
      self.uv_index()

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

   def uv_index(self):
      danger = 3;
      dangerous_hours = list(filter(lambda hr : hr.uv >= danger, self.doc.weather))
      if (len(dangerous_hours) > 0):
         for split in split_hours(dangerous_hours):
            warning = f'Wear sunscreen. The UV-index is high today from {split[0].date.strftime("%-I %p")} until {split[-1].date.strftime("%-I %p")}'
            self.topics.append(warning)
            

# needs to be tested still
def split_hours(hrs):
   """
   takes a list of Weather objects and splits them into groups of consecutive hours
   i.e. Weather objects whose hours are as follows: 
      [1, 2, 5, 6, 9] would be split into [[1, 2], [5, 6], [9]]
   """
   splits = list()
   curr_split = list()
   for hr in hrs:
      if (len(curr_split) == 0) or (int(curr_split[-1].date.hour) + 1 == int(hr.date.hour)):
         curr_split.append(hr)
      else:
         splits.append(curr_split)
         curr_split.clear()
   splits.append(curr_split)
   return splits


      
