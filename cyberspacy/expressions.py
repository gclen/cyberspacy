# Taken from Regular Expressions Cookbook 2nd edition by Levithan and Goyvaerts
ipv4_expr = r"""
(?:
(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.
(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.
(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.
(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])
)
"""

# Taken from Regular Expressions Cookbook 2nd edition by Levithan and Goyvaerts
ipv6_expr = r"""
(?:
# Mixed
 (?:
  # Non-compressed
  (?:[A-F0-9]{1,4}:){6}
  # Compressed with at most 6 colons
 |(?=(?:[A-F0-9]{0,4}:){0,6}
     (?:[0-9]{1,3}\.){3}[0-9]{1,3}  # and 4 bytes
     (?![:.\w]))                    # and anchored
  # and at most 1 double colon
  (?:(?:[0-9A-F]{1,4}:){0,5}|:)(?:(?::[0-9A-F]{1,4}){1,5}:|:)
  # Compressed with 7 colons and 5 numbers
 |::(?:[A-F0-9]{1,4}:){5}
 )
 # 255.255.255.
 (?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}
 # 255
 (?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])
|# Standard
 (?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}
|# Compressed with at most 7 colons
 (?=(?:[A-F0-9]{0,4}:){0,7}[A-F0-9]{0,4}
    (?![:.\w]))  # and anchored
 # and at most 1 double colon
 (?:(?:[0-9A-F]{1,4}:){1,7}|:)(?:(?::[0-9A-F]{1,4}){1,7}|:)
 # Compressed with 8 colons
|(?:[A-F0-9]{1,4}:){7}:|:(?::[A-F0-9]{1,4}){7}
)
"""

email_expr = r"""[\w!#$%&'*+/=?`{|}~^-]+(?:\.[\w!#$%&'*+/=?`{|}~^-]+)*@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}"""

url_expr = r"""
(?:(?:(?:(?:
  (?:ht|f)tp(?:s?)://|~/)
  (?:[-;:&=+$,\w'.]+@)?
  (?:[A-Za-z0-9.-:]+))
  |(?:(?:www\.|[-;:&=+$,\w'.]+@)
  (?:[A-Za-z0-9.-:]+))|
  (?:(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})))
  (?:[-\w~!$+|.,=/\?'#%*:&@;]*))
"""

