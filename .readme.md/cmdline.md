<!--
    $ export COLUMNS=120
-->

    $ strava-gear --help
    Usage: strava-gear [OPTIONS]
    
    Options:
      --rules FILENAME                Rules configuration (bikes, components, ...)  [default:
                                      /home/user/.config/strava_gear/rules.yaml]
    
      --csv FILENAME                  Load activities from CSV instead of the strava-offline database (columns: name,
                                      gear_id, start_date, moving_time, distance)
    
      --strava-database PATH          Location of the strava-offline database  [default:
                                      /home/user/.local/share/strava_offline/strava.sqlite]
    
      -o, --output FILENAME           Output file  [default: -]
      -r, --report [components|bikes]
                                      Type of report  [default: bikes]
      -f, --tablefmt TEXT             Table format, see <https://github.com/astanin/python-tabulate#table-format>.
                                      Additionally, "csv" is supported for CSV output.  [default: simple]
    
      --show-name / --hide-name       Show long component names  [default: True]
      --show-first-last / --hide-first-last
                                      Show first/last usage of components  [default: True]
      --help                          Show this message and exit.