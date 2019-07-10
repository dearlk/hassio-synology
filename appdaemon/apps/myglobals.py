notify_service = "zanzito_lalit"
#announcement_mode = self.get_state("input_boolean.announcement_mode")
#sleep_mode = self.get_state("binary_sensor.sleep_mode")

def logger (self, flag=0):
  if flag == 1:
    self.notify(self.message, name=notify_service)
    self.set_state("sensor.appd_notify",state=self.message, attributes={"announce":True})
  else:
    self.log(self.message)




