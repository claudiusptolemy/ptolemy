from string import Template

class Location(object):
    """Represents a Ptolemaic location, containing both the Ptolemaic 
    name and coordinates as well as the modern name and coordinates if
    known. Along with the modern information are status fields indicating
    the degree of certainty to which we feel the modern location is
    correct. Finally, there is a type field which indicates the type of
    geographical feature represented by this location object."""

    valid_init_args = set([
        'ptol_name',
        'ptol_lon',
        'ptol_lat',
        'object_type',
        'object_status',
        'modern_name',
        'modern_lon',
        'modern_lat'])
    
    def __init__(self, **args):
        """Constructs a new location object."""
        for key in args:
            if key in Location.valid_init_args:
                setattr(self, key, args[key])

    def __str__(self):
        """Return a comprehensive string representation of the location
        suitable for debugging."""
        pstring = ','.join('%s=%s' % (k,v) for (k,v) in vars(self).iteritems())
        return ('<Location %s>' % pstring).encode('ascii', 'ignore')

    @property
    def ptol_coords(self):
        return (self.ptol_lon, self.ptol_lat)

    @property
    def modern_coords(self):
        return (self.modern_lon, self.modern_lat)
        
    description_template = Template(
        """<table>
        <tr><td>Ptolemaic name</td><td>$ptol_name</td></tr>
        <tr><td>Ptolemaic longitude</td><td>$ptol_lon</td></tr>
        <tr><td>Ptolemaic latitude</td><td>$ptol_lat</td></tr>
        <tr><td>Modern name</td><td>$modern_name</td></tr>
        <tr><td>Modern longitude</td><td>$modern_lon</td></tr>
        <tr><td>Modern latitude</td><td>$modern_lat</td></tr>
        <tr><td>Object type</td><td>$object_type</td></tr>
        <tr><td>Object status</td><td>$object_status</td></tr>
        </table>
        """)
    
    @property
    def description(self):
        return Location.description_template.substitute(self)

    def __getitem__(self, name):
        return getattr(self, name)

    # map location status to colors for display according to
    # the KML color format (alpha, blue, green, red)
    status_colors = {
        'certain':     'ff00ff00',
        'tentative':   'ff00ffff',
        'approximate': 'ff00aaff',
        'duplicate':   'ffaaaaaa',
        'unprocessed': 'ffff00ff'}

    @property
    def object_status_color(self):
        return Location.status_colors[self.object_status]

