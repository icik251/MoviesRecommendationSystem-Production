test = '<< +albino+ >> << +catholicism+ >> << +christian+ >> << +conspiracy+ >> << +deadly+ >> << +deceit+ >> << ' \
       '+fame+ >> << +hall+ >> << +harvard+ >> << +heresy+ >> << +louvre+ >> << +mason+ >> << +monk+ >> << +murder+ ' \
       '>> << +museum+ >> << +paris+ >> << +pentagram+ >> << +piece+ >> << +professor+ >> << +robert+ >> << +sect+ >> ' \
       '<< +tomb+ >> << +web+ >> << +work+ >> << 2000_to_2010 >> << actoraudreytautou >> << actorianmckellen >> << ' \
       'actortomhanks >> << based+on+novel >> << composerhanszimmer >> << directorronhoward >> << genremystery >> << ' \
       'genrethriller >> << holy+grail >> << leonardo+da+vinci >> << producerbriangrazer >> << producerjohncalley >> ' \
       '<< producerkathleenmcgill >> << producerlouisavelis >> << producerronhoward >> << runtime_above_110 >> << ' \
       'screenplayakivagoldsman >> << secret+society >> '


test = test.replace('<<', '')
test = test.replace('>>', '')

print(test.strip())