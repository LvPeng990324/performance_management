class PageInfo(object):
    def __init__(self, current_page, all_count, per_page, base_url, show_page=7):
        try:
            self.current_page = int(current_page)
        except:
            self.current_page = 1
        self.per_page = per_page
        a, b = divmod(all_count, per_page)
        if b:
            a = a + 1
        self.all_page = a
        self.show_page = show_page
        self.base_url = base_url

    def start(self):
        return (self.current_page - 1) * self.per_page

    def end(self):
        return self.current_page * self.per_page

    def pager(self):
        page_list = []
        # 加入首页
        if self.current_page == 1:
            first_page = "<li><a href='javascript:void(0)'>首页</a></li>"
        else:
            first_page = "<li><a href='%spage=1'>首页</a></li>" % self.base_url
        page_list.append(first_page)
        half = int((self.show_page - 1) / 2)
        # 如果数据总页数<最大展示页数
        if self.all_page < self.show_page:
            begin = 1
            stop = self.all_page + 1
        # 如果数据总页数>最大展示页数
        else:
            # 如果当前页<=5,显示1-最大展示页数
            if self.current_page <= half:
                begin = 1
                stop = self.show_page + 1
            else:
                if self.current_page + half > self.all_page:
                    begin = self.all_page - self.show_page
                    stop = self.all_page + 1
                else:
                    begin = self.current_page - half
                    stop = self.current_page + half + 1
        if self.current_page <= 1:
            prev_page = "<li><a href='javascript:void(0)'>上一页</a></li>"
            page_list.append(prev_page)
        else:
            prev_page = "<li><a href='%spage=%s'>上一页</a></li>" % (self.base_url, self.current_page - 1)
            page_list.append(prev_page)
        for i in range(begin, stop):
            if i == self.current_page:
                temp = "<li class='active'><a href='javascript:void(0)'>%s</a></li>" % i
            else:
                temp = "<li><a href='%spage=%s'>%s</a></li>" % (self.base_url, i, i)
            page_list.append(temp)

        if self.current_page >= self.all_page:
            next_page = "<li><a href='javascript:void(0)'>下一页</a></li>"
            page_list.append(next_page)
        else:
            next_page = "<li><a href='%spage=%s'>下一页</a></li>" % (self.base_url, self.current_page + 1)
            page_list.append(next_page)
        # 加入尾页
        if self.current_page == self.all_page or self.all_page == 0:
            last_page = "<li><a href='javascript:void(0)'>尾页</a></li>"
        else:
            last_page = "<li><a href='%spage=%s'>尾页</a></li>" % (self.base_url, self.all_page)
        page_list.append(last_page)
        return ' '.join(page_list)
