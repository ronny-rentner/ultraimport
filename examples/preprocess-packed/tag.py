from packed import Component, packed

class ShareLink(Component):

   def render(self):
      return <a href={self.props['link']}>Share on internet</a>

@packed
def tag(self):
    share = get_share_link()
    return <ShareLink link={share} />
