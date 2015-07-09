from igram.utils.search import InstagramSearch
from igram import results
from graph import draw_graph


tags = ['gronk']


def page_rank_tags(tags, pages=10, related_tags=2, num_tags=25, min_weight=3):
    all_media = {}
    for tag in tags:
        iSearch = InstagramSearch()
        if related_tags:
            similar_tags = iSearch.tag_search(tag)[0][:related_tags]
            print similar_tags
            if similar_tags:
                similar_tags = [tg.name for tg in similar_tags]
            else:
                similar_tags = [tag]
            print "searching for {0} similar tags {1}".format(related_tags, "\t".join(similar_tags))
        else:
            similar_tags = [tag]
        for t in similar_tags:
            res = iSearch.tag_recent_media(t, pages=pages)
            all_media.update(res)
    # {'tag_info': tag_info, 'tag_page_rank': tpr, 'graph': graph}
    result = results.run_tag_pagerank(all_media, num_tags, min_weight)
    tag_info = result['tag_info']
    tag_page_rank = result['tag_page_rank']
    graph = result['graph']
    draw_graph(graph, file_name="{0}.png".format('_'.join(tags)), rank=tag_page_rank)
    results.print_page_rank(tag_page_rank, tag_info)


page_rank_tags(tags, 5)
