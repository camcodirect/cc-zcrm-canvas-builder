# Canvas key inventory (generated)

Generated from 33 Zoho-authored canvas payloads: 3 gallery templates and 30 consecutive editor saves. Every key that appears anywhere in a canvas_view, grouped by the slot it lives in. `count` is occurrences across all files; `hosts` are the node kinds (type/theme) that carry it; `samples` are the most common values. Regenerate with the inventory script rather than editing by hand.


## `node`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `ui` | 15280 | field/None (5438), None/None (4995), component/Custom Layout (1028), row/None (1008) … | dict | `{field,holder,label,value}` ×5051<br>`{value}` ×2947<br>`{index,value}` ×1675<br>`{field,value}` ×622 |
| `type` | 10285 | field/None (5438), component/Custom Layout (1028), row/None (1008), component/Static Text (541) … | str | `"field"` ×5438<br>`"component"` ×2038<br>`"row"` ×1008<br>`"action"` ×480 |
| `uniqueid` | 6884 | field/None (1856), row/None (999), component/Custom Layout (992), component/Static Text (526) … | str | `"e825e4c3-8774-4ac0-9be1-00884fb312ae"` ×35<br>`"7ee13e61-3f06-4780-a876-e893bb54bab8"` ×35<br>`"282624ba-0ac3-48cb-b2ad-2d0ee9476b9a"` ×35<br>`"bbcdad37-3f61-4e10-97ef-e498ae275d32"` ×35 |
| `id` | 6669 | field/None (5428), action/None (480), section/None (332), relatedlist/Table Layout (207) … | str | `"commonfield"` ×332<br>`"2582206000000002295"` ×96<br>`"2582206000000096001"` ×96<br>`"2582206000000096003"` ×96 |
| `datatype` | 5588 | field/None (5102), action/None (480), link/None (5), button/None (1) | str | `"text"` ×1772<br>`"picklist"` ×710<br>`"date-time"` ×700<br>`"button"` ×481 |
| `theme` | 2799 | component/Custom Layout (1028), component/Static Text (541), static_content/Custom Layout (427), relatedlist/Table Layout (207) … | str | `"Custom Layout"` ×1650<br>`"Static Text"` ×541<br>`"Table Layout"` ×378<br>`"Tab Layout"` ×65 |
| `related_list` | 428 | component/Custom Layout (428) | bool | `true` ×428 |
| `static_id` | 332 | section/None (332) | str | `"Address Information"` ×33<br>`"Contact Information"` ×31<br>`"Email Verification"` ×31<br>`"RE Fields"` ×31 |
| `tab_relatedlist_id` | 219 | component/Custom Layout (219) | str | `"timeline"` ×33<br>`"2582206000000003801"` ×31<br>`"2582206000025002875"` ×31<br>`"2582206000000015214"` ×31 |
| `details` | 35 | field/None (18), component/Custom Layout (12), relatedlist/Custom Layout (5) | dict | `{connection_id,connection_type}` ×17<br>`{connection_id,connection_type,path}` ×10<br>`{connection_id,connection_type,id}` ×8 |
| `personality_name` | 34 | relatedlist/Table Layout (34) | str | `"EMAILSPERSONALITY"` ×32<br>`"ZINVOICEPERSONALITY"` ×1<br>`"PROJECTSPERSONALITY"` ×1 |
| `name` | 33 | ROOT (33) | str | `"canvas template 3"` ×31<br>`"Canvas-template 2"` ×1<br>`"Main Account"` ×1 |
| `feature` | 33 | ROOT (33) | str | `"DetailView"` ×33 |
| `module` | 33 | ROOT (33) | dict | `{api_name,id}` ×33 |
| `layout` | 33 | ROOT (33) | dict | `{id}` ×33 |
| `state` | 33 | ROOT (33) | str | `"active"` ×33 |
| `action` | 33 | ROOT (33) | str | `"edit"` ×33 |
| `related_to` | 33 | ROOT (33) | dict | `{data_hub_associations,homepage_associations,lookup_assoc}` ×33 |

## `ui`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `value` | 13288 | field/None (5438), None/None (3335), component/Custom Layout (1028), row/None (1008) … | dict | `{class,custom_style,position,style}` ×7095<br>`{style}` ×1675<br>`{}` ×1660<br>`{class,custom_style,position,style,value}` ×542 |
| `field` | 6291 | field/None (5438), action/None (480), None/None (332), component/Canvas Button (28) … | dict | `{class,custom_style,style}` ×5597<br>`{custom_style,style}` ×362<br>`{width}` ×332 |
| `holder` | 5301 | field/None (5051), action/None (249), link/None (1) | dict | `{class,custom_style,style}` ×4968<br>`{custom_style,style}` ×333 |
| `label` | 5080 | field/None (5051), table_cell/None (29) | dict | `{class,custom_style,style}` ×4718<br>`{custom_style,style}` ×362 |
| `index` | 1675 | None/None (1675) | int | `0` ×332<br>`1` ×301<br>`2` ×268<br>`3` ×195 |
| `autoheight` | 541 | component/Static Text (541) | bool | `false` ×425<br>`true` ×116 |
| `canvas_rules` | 461 | relatedlist/Table Layout (207), relatedlist/Custom Layout (195), ROOT (33), relatedlist/Canvas Data Table (26) | list | `list[0]` ×461 |
| `row` | 358 | None/None (332), relatedlist/Canvas Data Table (26) | dict | `{height}` ×332<br>`{custom_style,style}` ×26 |
| `layoutstyle` | 358 | None/None (332), relatedlist/Canvas Data Table (26) | dict | `{field,inner,row}` ×332<br>`{head,row}` ×26 |
| `tab_item_title` | 348 | component/Custom Layout (346), component/Tab Layout (2) | dict | `{class}` ×348 |
| `sectionstyle` | 332 | None/None (332) | dict | `{value}` ×332 |
| `titlesection` | 332 | None/None (332) | dict | `{children,theme,type,ui,uniqueid}` ×321<br>`{children,theme,type,ui}` ×11 |
| `datastyle` | 332 | None/None (332) | dict | `{}` ×332 |
| `datastylefields` | 332 | None/None (332) | dict | `{}` ×332 |
| `datastylerow` | 332 | None/None (332) | dict | `{}` ×332 |
| `datastylelayout` | 332 | None/None (332) | dict | `{}` ×332 |
| `inner` | 332 | None/None (332) | list | `list[2]` ×311<br>`list[1]` ×21 |
| `datastyletable` | 332 | None/None (332) | dict | `{}` ×332 |
| `style` | 332 | None/None (332) | dict | `{default}` ×332 |
| `custom_style` | 332 | None/None (332) | dict | `{}` ×332 |
| `position` | 332 | None/None (332) | dict | `{depth,end_x,height,start_x,start_y,width}` ×228<br>`{depth,end_x,height,min_top,start_x,start_y,width}` ×104 |
| `tagname` | 332 | None/None (332) | str | `"DIV"` ×332 |
| `class` | 332 | None/None (332) | str | `"zclayout-table zcrestricttable zcnochange"` ×332 |
| `icon` | 250 | action/None (249), link/None (1) | dict | `{class,custom_style,icon,style}` ×250 |
| `context` | 100 | relatedlist/Table Layout (100) | dict | `{timeline_content,timeline_date,timeline_footer,timeline_}` ×64<br>`{notes_content,notes_footer,notes_link,notes_separator,no}` ×32<br>`{table_column,table_head,table_link,table_row}` ×3<br>`{notes_content,notes_footer,notes_link,notes_title}` ×1 |
| `header` | 55 | table_cell/None (29), relatedlist/Canvas Data Table (26) | dict | `{custom_style,style}` ×55 |
| `allfieldstabstyle` | 45 | component/Custom Layout (45) | dict | `{}` ×45 |
| `script_info` | 33 | ROOT (33) | dict | `{deleted,mapping}` ×33 |
| `column` | 29 | table_cell/None (29) | dict | `{custom_style,style}` ×29 |
| `column_odd` | 29 | table_cell/None (29) | dict | `{custom_style,style}` ×29 |
| `column_even` | 29 | table_cell/None (29) | dict | `{custom_style,style}` ×29 |
| `field_odd` | 29 | field/None (29) | dict | `{custom_style,style}` ×29 |
| `field_even` | 29 | field/None (29) | dict | `{custom_style,style}` ×29 |
| `row_odd` | 26 | relatedlist/Canvas Data Table (26) | dict | `{custom_style,style}` ×26 |
| `row_even` | 26 | relatedlist/Canvas Data Table (26) | dict | `{custom_style,style}` ×26 |
| `static_column_value` | 26 | relatedlist/Canvas Data Table (26) | dict | `{class,fixed,position,style}` ×26 |
| `static_column_label` | 26 | relatedlist/Canvas Data Table (26) | dict | `{custom_style,style}` ×26 |
| `static_column_header` | 26 | relatedlist/Canvas Data Table (26) | dict | `{custom_style,style}` ×26 |
| `static_column_column` | 26 | relatedlist/Canvas Data Table (26) | dict | `{custom_style,style}` ×26 |
| `static_column_column_odd` | 26 | relatedlist/Canvas Data Table (26) | dict | `{custom_style,style}` ×26 |
| `static_column_column_even` | 26 | relatedlist/Canvas Data Table (26) | dict | `{custom_style,style}` ×26 |
| `image` | 7 | component/Canvas Image (7) | dict | `{style}` ×7 |

## `ui.value`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 11628 | field/None (5438), None/None (1675), component/Custom Layout (1028), row/None (1008) … | dict | `{default}` ×10914<br>`{}` ×712<br>`{default,hover}` ×2 |
| `position` | 9953 | field/None (5438), component/Custom Layout (1028), row/None (1008), component/Static Text (541) … | dict | `{depth,end_x,height,order,start_x,start_y,width}` ×5248<br>`{depth,end_x,height,start_x,start_y,width}` ×2925<br>`{depth,end_x,height,min_left,min_top,start_x,start_y,widt}` ×1022<br>`{depth,end_x,height,min_left,min_top,order,start_x,start_}` ×340 |
| `custom_style` | 9686 | field/None (5409), component/Custom Layout (1028), row/None (1008), component/Static Text (540) … | dict | `{}` ×9686 |
| `class` | 9347 | field/None (5071), component/Custom Layout (1028), row/None (1008), component/Static Text (541) … | str | `"zcanvas-field"` ×2852<br>`"zcanvas-row"` ×1008<br>`"zcanvas-field zc-rl-field zc-ta-left"` ×719<br>`"zcanvas-title-editor"` ×428 |
| `zcode` | 851 | component/Custom Layout (651), component/Static Text (94), component/Tab Layout (63), component/Flex Layout (10) … | dict | `{name}` ×851 |
| `value` | 637 | component/Static Text (541), separator/None (96) | str | `""` ×96<br>`"<span style=\"font-family: Zoho_Puvi_ExtraBold;\">CARD TITL` ×52<br>`"AI Meeting Extractions"` ×50<br>`"Open Tasks"` ×36 |
| `related_list` | 428 | component/Custom Layout (428) | bool | `true` ×428 |
| `editorclass` | 428 | component/Custom Layout (428) | str | `"zcanvas-loading-component"` ×428 |
| `name` | 376 | component/Custom Layout (346), component/Canvas Button (28), component/Tab Layout (2) | str | `"Notes"` ×33<br>`"Timeline"` ×33<br>`"All Fields"` ×33<br>`"Overview"` ×32 |
| `count` | 284 | component/Custom Layout (284) | str | `"5"` ×216<br>`"10"` ×68 |
| `recordcount` | 284 | relatedlist/Custom Layout (185), relatedlist/Table Layout (73), relatedlist/Canvas Data Table (26) | str | `"5"` ×216<br>`"10"` ×68 |
| `disabled` | 264 | component/Custom Layout (264) | bool | `true` ×264 |
| `layoutstyle` | 236 | component/Table Layout (171), component/Tab Layout (65) | dict | `{field,inner,row}` ×171<br>`{active,container,default,editor,hover,tabicon,tabname}` ×65 |
| `fixed` | 204 | component/Custom Layout (94), field/None (62), table_cell/None (29), component/Static Icon (7) … | bool | `true` ×146<br>`false` ×58 |
| `scope` | 171 | component/Table Layout (171) | str | `"default"` ×171 |
| `icon` | 69 | component/Custom Layout (62), component/Static Icon (7) | str | `"icon-Icon_plus"` ×31<br>`"icon-Icon_Back"` ×31<br>`"icon-Icon_Fiber"` ×2<br>`"icon-Icon_Customerprofile"` ×1 |
| `custom_layoutstyle` | 65 | component/Tab Layout (65) | dict | `{active,container,default,editor,hover,tabicon,tabname}` ×65 |
| `property` | 40 | component/Flex Layout (18), component/Grid Layout (9), component/Table Layout (8), component/Custom Layout (5) | dict | `{flex}` ×18<br>`{flex_item}` ×13<br>`{grid}` ×9 |
| `list_type_class` | 5 | relatedlist/Custom Layout (5) | str | `"zc-rl-cards"` ×5 |
| `list_type_width` | 5 | relatedlist/Custom Layout (5) | int | `596` ×2<br>`413` ×1<br>`545` ×1<br>`611` ×1 |
| `vertical` | 5 | component/Line (5) | bool | `false` ×5 |

## `ui.value.position`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `start_x` | 9915 | field/None (5438), component/Custom Layout (1028), row/None (1008), component/Static Text (541) … | int | `0` ×5985<br>`30` ×876<br>`10` ×453<br>`17` ×243 |
| `start_y` | 9915 | field/None (5438), component/Custom Layout (1028), row/None (1008), component/Static Text (541) … | int | `0` ×5108<br>`30` ×537<br>`11` ×424<br>`80` ×364 |
| `end_x` | 9915 | field/None (5438), component/Custom Layout (1028), row/None (1008), component/Static Text (541) … | int | `297` ×2891<br>`237` ×559<br>`286` ×451<br>`295` ×435 |
| `width` | 9915 | field/None (5438), component/Custom Layout (1028), row/None (1008), component/Static Text (541) … | int | `297` ×2830<br>`237` ×558<br>`295` ×434<br>`286` ×420 |
| `height` | 9915 | field/None (5438), component/Custom Layout (1028), row/None (1008), component/Static Text (541) … | int | `50` ×3461<br>`30` ×979<br>`19` ×502<br>`32` ×436 |
| `depth` | 9915 | field/None (5438), component/Custom Layout (1028), row/None (1008), component/Static Text (541) … | int | `1` ×9409<br>`2` ×207<br>`4` ×95<br>`5` ×93 |
| `order` | 5588 | field/None (4219), row/None (1008), component/Custom Layout (351), component/Table Layout (8) … | int | `0` ×2897<br>`1` ×1778<br>`2` ×201<br>`3` ×167 |
| `min_left` | 1517 | component/Custom Layout (887), static_content/Custom Layout (426), relatedlist/Custom Layout (195), component/Flex Layout (8) … | int | `30` ×485<br>`10` ×418<br>`20` ×108<br>`29` ×64 |
| `min_top` | 1492 | component/Custom Layout (857), static_content/Custom Layout (426), relatedlist/Custom Layout (195), component/Flex Layout (8) … | int | `30` ×439<br>`11` ×358<br>`13` ×126<br>`10` ×77 |
| `over_top` | 212 | component/Custom Layout (85), action/None (66), component/Tab Layout (58), field/None (3) | int | `-4` ×40<br>`-69` ×31<br>`-44` ×31<br>`-47` ×31 |
| `_locked_` | 103 | component/Custom Layout (102), component/Tab Layout (1) | str | `"true"` ×103 |
| `over_left` | 66 | component/Custom Layout (62), field/None (4) | int | `-22` ×31<br>`-10` ×31<br>`-75` ×3<br>`-12` ×1 |

## `ui.value.zcode`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `name` | 851 | component/Custom Layout (651), component/Static Text (94), component/Tab Layout (63), component/Flex Layout (10) … | str | `"section1"` ×64<br>`"tab1"` ×63<br>`"RL-AI Meeting Extractions"` ×50<br>`"RL-Open Tasks"` ×36 |

## `ui.value.property`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `flex` | 18 | component/Flex Layout (18) | dict | `{}` ×10<br>`{default}` ×8 |
| `flex_item` | 13 | component/Table Layout (8), component/Custom Layout (5) | dict | `{default}` ×13 |
| `grid` | 9 | component/Grid Layout (9) | dict | `{default}` ×9 |

## `ui.value.property.flex.default`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `direction` | 8 | component/Flex Layout (8) | str | `"column"` ×8 |
| `space_distribute` | 8 | component/Flex Layout (8) | str | `"_normal"` ×4<br>`"normal_normal"` ×4 |
| `alignment` | 8 | component/Flex Layout (8) | str | `"topleft"` ×8 |
| `wrap` | 8 | component/Flex Layout (8) | str | `"nowrap"` ×8 |

## `ui.value.property.flex_item.default`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `h_stretch` | 13 | component/Table Layout (8), component/Custom Layout (5) | bool | `true` ×8<br>`false` ×5 |
| `v_stretch` | 13 | component/Table Layout (8), component/Custom Layout (5) | bool | `false` ×13 |
| `align_self` | 13 | component/Table Layout (8), component/Custom Layout (5) | str | `""` ×13 |

## `ui.value.property.grid.default`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `column_gap` | 9 | component/Grid Layout (9) | str | `"5px"` ×9 |
| `row_gap` | 9 | component/Grid Layout (9) | str | `"5px"` ×9 |
| `block_width_count` | 9 | component/Grid Layout (9) | list | `list[1]` ×9 |
| `block_height_px` | 9 | component/Grid Layout (9) | str | `"20px"` ×9 |

## `ui.value.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 10916 | field/None (5409), None/None (1675), row/None (1008), component/Custom Layout (655) … | dict | `{}` ×9062<br>`{font_family,font_size,padding}` ×372<br>`{border,border_radius,box_shadow}` ×360<br>`{background_color}` ×250 |
| `hover` | 2 | action/None (2) | dict | `{background_image,border,color}` ×2 |

## `ui.value.layoutstyle`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `field` | 171 | component/Table Layout (171) | dict | `{width}` ×171 |
| `row` | 171 | component/Table Layout (171) | dict | `{height}` ×171 |
| `inner` | 171 | component/Table Layout (171) | list | `list[1]` ×171 |
| `default` | 65 | component/Tab Layout (65) | dict | `{}` ×32<br>`{background_color,border_bottom,border_bottom_left_radius}` ×31<br>`{border_top,color,padding_bottom,padding_left,padding_rig}` ×1<br>`{border_bottom,border_top}` ×1 |
| `hover` | 65 | component/Tab Layout (65) | dict | `{}` ×33<br>`{border_bottom,border_bottom_left_radius,border_bottom_ri}` ×31<br>`{background_color,border_bottom,border_bottom_left_radius}` ×1 |
| `active` | 65 | component/Tab Layout (65) | dict | `{}` ×32<br>`{background_color,border_bottom,border_bottom_right_radiu}` ×31<br>`{border_bottom,color,padding_bottom,padding_left,padding_}` ×1<br>`{background_color,border_bottom,border_radius,color,font_}` ×1 |
| `container` | 65 | component/Tab Layout (65) | dict | `{default}` ×54<br>`{}` ×11 |
| `editor` | 65 | component/Tab Layout (65) | dict | `{default}` ×56<br>`{}` ×9 |
| `tabname` | 65 | component/Tab Layout (65) | dict | `{active,default,hover}` ×33<br>`{default}` ×21<br>`{}` ×11 |
| `tabicon` | 65 | component/Tab Layout (65) | dict | `{}` ×35<br>`{default}` ×30 |

## `style.<state>.*`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `font_size` | 3888 | field/None (3247), component/Static Text (374), action/None (249), link/None (10) … | str | `"14px"` ×2721<br>`"16px"` ×470<br>`"15px"` ×451<br>`"18px"` ×136 |
| `color` | 3203 | field/None (2720), action/None (344), component/Tab Layout (132), component/Static Icon (5) … | str | `"rgba(133, 141, 156, 1)"` ×1078<br>`"rgba(10, 31, 55, 1)"` ×1035<br>`"rgba(255, 255, 255, 1)"` ×257<br>`"rgba(255, 117, 101, 1)"` ×128 |
| `font_family` | 1995 | field/None (1562), component/Static Text (389), action/None (37), component/Tab Layout (5) … | str | `"r"` ×1437<br>`"m"` ×439<br>`"b"` ×65<br>`"s"` ×53 |
| `padding_left` | 1831 | field/None (1489), action/None (276), component/Tab Layout (65), component/Static Text (1) | str | `"0px"` ×1641<br>`"20px"` ×62<br>`"15px"` ×31<br>`"14px"` ×31 |
| `background_color` | 1101 | action/None (379), component/Tab Layout (195), component/Table Layout (170), component/Custom Layout (156) … | str | `"rgba(255,255,255,0)"` ×282<br>`"transparent"` ×173<br>`"rgba(0,0,0,0)"` ×162<br>`"rgba(255, 255, 255, 0)"` ×132 |
| `border` | 995 | component/Custom Layout (554), action/None (350), field/None (64), component/Grid Layout (9) … | str | `"none"` ×711<br>`"1px solid rgba(236, 236, 238,1)"` ×84<br>`"1px solid rgb(245, 247, 249)"` ×62<br>`"1px solid rgb(17, 205, 142)"` ×31 |
| `border_radius` | 972 | component/Custom Layout (556), action/None (312), field/None (66), component/Tab Layout (20) … | str | `"20px"` ×341<br>`"0"` ×146<br>`"99px"` ×124<br>`"4px"` ×84 |
| `padding` | 868 | component/Static Text (468), component/Tab Layout (118), action/None (98), field/None (73) … | str | `"0px"` ×570<br>`"0"` ×70<br>`"3px"` ×62<br>`"5px"` ×40 |
| `padding_right` | 777 | field/None (434), action/None (276), component/Tab Layout (65), component/Custom Layout (1) … | str | `"0px"` ×462<br>`"20px"` ×94<br>`"10px"` ×93<br>`"15px"` ×31 |
| `$inherited` | 620 | field/None (620) | bool | `true` ×620 |
| `box_shadow` | 601 | component/Custom Layout (554), component/Tab Layout (19), component/Grid Layout (9), component/Flex Layout (8) … | str | `"none"` ×572<br>`"5px 5px 10px 0px rgba(0, 0, 0, 0.12)"` ×18<br>`"0px 0px 10px 0px rgba(0, 0, 0, 0.05)"` ×8<br>`"0px 2px 2px 0px rgba(0, 0, 0, 0.12)"` ×2 |
| `margin_left` | 573 | field/None (572), component/Tab Layout (1) | str | `"8px"` ×572<br>`"20px"` ×1 |
| `padding_bottom` | 497 | action/None (276), component/Tab Layout (127), field/None (93), component/Static Text (1) | str | `"0px"` ×97<br>`"15px"` ×95<br>`"5px"` ×94<br>`"8px"` ×94 |
| `padding_top` | 373 | action/None (276), component/Tab Layout (96), component/Static Text (1) | str | `"15px"` ×95<br>`"8px"` ×93<br>`"4px"` ×84<br>`"0px"` ×66 |
| `flex_direction` | 181 | field/None (181) | str | `"column"` ×181 |
| `width` | 171 | component/Table Layout (171) | str | `"100%"` ×171 |
| `height` | 171 | component/Table Layout (171) | str | `"30px"` ×66<br>`"29px"` ×34<br>`"32px"` ×31<br>`"27px"` ×31 |
| `_show_` | 106 | component/Custom Layout (94), component/Tab Layout (12) | str | `"true"` ×106 |
| `border_bottom` | 99 | component/Tab Layout (97), component/Custom Layout (2) | str | `"0px solid rgb(0, 0, 0)"` ×62<br>`"0px solid rgb(0, 112, 210)"` ×31<br>`"4px solid rgba(255, 255, 255, 0)"` ×2<br>`"3px solid rgb(45, 123, 209)"` ×1 |
| `border_top_right_radius` | 94 | component/Tab Layout (94) | str | `"12px"` ×93<br>`"0px"` ×1 |
| `border_top_left_radius` | 94 | component/Tab Layout (94) | str | `"12px"` ×93<br>`"0px"` ×1 |
| `border_bottom_right_radius` | 94 | component/Tab Layout (94) | str | `"0px"` ×94 |
| `line_height` | 64 | field/None (64) | float | `1.2` ×62<br>`1.1` ×1<br>`1.5` ×1 |
| `border_bottom_left_radius` | 63 | component/Tab Layout (63) | str | `"0px"` ×63 |
| `background_image` | 54 | component/Custom Layout (32), component/Canvas Image (12), action/None (7), component/Tab Layout (2) … | str | `"url(/crm/CRMClient/images/canvas/insura.png)"` ×31<br>`"none"` ×8<br>`"url($Image{2582206000076736002})"` ×6<br>`"linear-gradient(180deg , rgba(255, 168, 180, 1) 0%, rgba(25` ×2 |
| `vertical_align` | 42 | field/None (42) | str | `"top"` ×42 |
| `border_top` | 35 | component/Tab Layout (33), component/Custom Layout (2) | str | `"0px solid transparent"` ×33<br>`"0px solid rgb(228, 235, 239)"` ×1<br>`"0px solid rgb(221, 219, 218)"` ×1 |
| `margin_right` | 31 | component/Tab Layout (31) | str | `"5px"` ×31 |
| `_section_version_` | 30 | component/Custom Layout (30) | int | `1` ×30 |
| `margin` | 18 | component/Tab Layout (18) | str | `"21px"` ×18 |
| `src` | 6 | component/Canvas Image (6) | str | `"$Image{2582206000076736002}"` ×6 |
| `margin_top` | 4 | field/None (2), component/Tab Layout (2) | str | `"5px"` ×1<br>`"8px"` ×1<br>`"0px"` ×1<br>`"16px"` ×1 |
| `border_right` | 3 | component/Custom Layout (2), component/Tab Layout (1) | str | `"1px solid rgb(228, 235, 239)"` ×1<br>`"0px undefined rgb(62, 62, 60)"` ×1<br>`"0px solid rgb(221, 219, 218)"` ×1 |
| `text_transform` | 3 | component/Tab Layout (3) | str | `"uppercase"` ×2<br>`""` ×1 |
| `border_left` | 2 | component/Custom Layout (2) | str | `"1px solid rgb(228, 235, 239)"` ×1<br>`"0px solid rgb(221, 219, 218)"` ×1 |
| `background_size` | 1 | component/Custom Layout (1) | str | `"cover"` ×1 |
| `background_repeat` | 1 | component/Custom Layout (1) | str | `"repeat-y"` ×1 |
| `_hide_` | 1 | component/Tab Layout (1) | str | `"true"` ×1 |

## `ui.field`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 5959 | field/None (5438), action/None (480), component/Canvas Button (28), component/Canvas Image (7) … | dict | `{default}` ×5565<br>`{}` ×394 |
| `custom_style` | 5959 | field/None (5438), action/None (480), component/Canvas Button (28), component/Canvas Image (7) … | dict | `{}` ×5959 |
| `class` | 5597 | field/None (5076), action/None (480), component/Canvas Button (28), component/Canvas Image (7) … | str | `""` ×5534<br>`"zcanvasuppercase"` ×63 |
| `width` | 332 | None/None (332) | str | `"50%"` ×332 |

## `ui.holder`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 5301 | field/None (5051), action/None (249), link/None (1) | dict | `{default}` ×4954<br>`{}` ×347 |
| `custom_style` | 5301 | field/None (5051), action/None (249), link/None (1) | dict | `{}` ×5301 |
| `class` | 4968 | field/None (4718), action/None (249), link/None (1) | str | `""` ×4968 |

## `ui.label`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 5080 | field/None (5051), table_cell/None (29) | dict | `{default}` ×4708<br>`{}` ×372 |
| `custom_style` | 5080 | field/None (5051), table_cell/None (29) | dict | `{}` ×5080 |
| `class` | 4718 | field/None (4718) | str | `""` ×4717<br>`"zcanvasuppercase"` ×1 |

## `ui.icon`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 250 | action/None (249), link/None (1) | dict | `{default}` ×250 |
| `custom_style` | 250 | action/None (249), link/None (1) | dict | `{}` ×250 |
| `class` | 250 | action/None (249), link/None (1) | str | `""` ×250 |
| `icon` | 250 | action/None (249), link/None (1) | str | `"icon-Icon_dot_three"` ×215<br>`"icon-Icon_plus"` ×33<br>`"icon-Icon_Money"` ×1<br>`"icon-Icon_Status"` ×1 |

## `ui.image`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 7 | component/Canvas Image (7) | dict | `{default}` ×6<br>`{}` ×1 |

## `ui.tab_item_title`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `class` | 348 | component/Custom Layout (346), component/Tab Layout (2) | str | `""` ×346<br>`"zc-tabgroup"` ×2 |

## `ui.context`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `timeline_content` | 64 | relatedlist/Table Layout (64) | dict | `{}` ×64 |
| `timeline_footer` | 64 | relatedlist/Table Layout (64) | dict | `{}` ×64 |
| `timeline_owner_field` | 64 | relatedlist/Table Layout (64) | dict | `{}` ×64 |
| `timeline_new_value` | 64 | relatedlist/Table Layout (64) | dict | `{}` ×64 |
| `timeline_link` | 64 | relatedlist/Table Layout (64) | dict | `{}` ×64 |
| `timeline_date` | 64 | relatedlist/Table Layout (64) | dict | `{}` ×64 |
| `timeline_time` | 64 | relatedlist/Table Layout (64) | dict | `{}` ×64 |
| `timeline_old_value` | 64 | relatedlist/Table Layout (64) | dict | `{}` ×64 |
| `notes_footer` | 33 | relatedlist/Table Layout (33) | dict | `{}` ×33 |
| `notes_title` | 33 | relatedlist/Table Layout (33) | dict | `{}` ×33 |
| `notes_content` | 33 | relatedlist/Table Layout (33) | dict | `{}` ×33 |
| `notes_link` | 33 | relatedlist/Table Layout (33) | dict | `{}` ×32<br>`{color}` ×1 |
| `notes_separator` | 32 | relatedlist/Table Layout (32) | dict | `{}` ×32 |
| `table_row` | 3 | relatedlist/Table Layout (3) | dict | `{}` ×3 |
| `table_link` | 3 | relatedlist/Table Layout (3) | dict | `{}` ×3 |
| `table_column` | 3 | relatedlist/Table Layout (3) | dict | `{}` ×3 |
| `table_head` | 3 | relatedlist/Table Layout (3) | dict | `{}` ×3 |

## `ui.header`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 55 | table_cell/None (29), relatedlist/Canvas Data Table (26) | dict | `{default}` ×45<br>`{}` ×10 |
| `custom_style` | 55 | table_cell/None (29), relatedlist/Canvas Data Table (26) | dict | `{}` ×55 |

## `ui.row`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `height` | 332 | None/None (332) | str | `"50px"` ×330<br>`"39px"` ×1<br>`"31px"` ×1 |
| `style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{default}` ×21<br>`{}` ×5 |
| `custom_style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{}` ×26 |

## `ui.row_odd`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{default}` ×21<br>`{}` ×5 |
| `custom_style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{}` ×26 |

## `ui.row_even`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{default}` ×21<br>`{}` ×5 |
| `custom_style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{}` ×26 |

## `ui.column`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 29 | table_cell/None (29) | dict | `{default}` ×24<br>`{}` ×5 |
| `custom_style` | 29 | table_cell/None (29) | dict | `{}` ×29 |

## `ui.column_odd`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 29 | table_cell/None (29) | dict | `{default}` ×24<br>`{}` ×5 |
| `custom_style` | 29 | table_cell/None (29) | dict | `{}` ×29 |

## `ui.column_even`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 29 | table_cell/None (29) | dict | `{default}` ×24<br>`{}` ×5 |
| `custom_style` | 29 | table_cell/None (29) | dict | `{}` ×29 |

## `ui.field_odd`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 29 | field/None (29) | dict | `{default}` ×24<br>`{}` ×5 |
| `custom_style` | 29 | field/None (29) | dict | `{}` ×29 |

## `ui.field_even`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 29 | field/None (29) | dict | `{default}` ×24<br>`{}` ×5 |
| `custom_style` | 29 | field/None (29) | dict | `{}` ×29 |

## `ui.layoutstyle`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `row` | 358 | None/None (332), relatedlist/Canvas Data Table (26) | dict | `{height}` ×332<br>`{$height}` ×26 |
| `field` | 332 | None/None (332) | dict | `{width}` ×332 |
| `inner` | 332 | None/None (332) | list | `list[2]` ×311<br>`list[1]` ×21 |
| `head` | 26 | relatedlist/Canvas Data Table (26) | dict | `{$height}` ×26 |

## `ui.sectionstyle`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `value` | 332 | None/None (332) | dict | `{class,custom_style,editorclass,position,related_list,sty}` ×332 |

## `ui.titlesection`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `ui` | 332 | None/None (332) | dict | `{value}` ×332 |
| `children` | 332 | None/None (332) | list | `list[1]` ×332 |
| `type` | 332 | None/None (332) | str | `"static_content"` ×332 |
| `theme` | 332 | None/None (332) | str | `"Custom Layout"` ×332 |
| `uniqueid` | 321 | None/None (321) | str | `"3ee5d8b3-92c0-41db-a2b7-c77bfd2ea454"` ×31<br>`"7db0ae39-2fee-4740-8355-fa704f7e3466"` ×31<br>`"395a9170-a083-455a-8685-3af8b4d74422"` ×31<br>`"b30054bb-b92a-473f-a308-dc89d6da7d62"` ×31 |

## `ui.static_column_value`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{}` ×26 |
| `class` | 26 | relatedlist/Canvas Data Table (26) | str | `""` ×26 |
| `position` | 26 | relatedlist/Canvas Data Table (26) | dict | `{depth,end_x,height,start_x,start_y,width}` ×26 |
| `fixed` | 26 | relatedlist/Canvas Data Table (26) | bool | `false` ×26 |

## `ui.static_column_label`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{default}` ×21<br>`{}` ×5 |
| `custom_style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{}` ×26 |

## `ui.static_column_header`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{default}` ×21<br>`{}` ×5 |
| `custom_style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{}` ×26 |

## `ui.static_column_column`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{default}` ×21<br>`{}` ×5 |
| `custom_style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{}` ×26 |

## `ui.static_column_column_odd`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{default}` ×21<br>`{}` ×5 |
| `custom_style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{}` ×26 |

## `ui.static_column_column_even`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{default}` ×21<br>`{}` ×5 |
| `custom_style` | 26 | relatedlist/Canvas Data Table (26) | dict | `{}` ×26 |

## `ui.script_info`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `mapping` | 33 | ROOT (33) | dict | `{}` ×33 |
| `deleted` | 33 | ROOT (33) | list | `list[0]` ×33 |

## `ui.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 332 | None/None (332) | dict | `{}` ×332 |

## `ui.position`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `start_x` | 332 | None/None (332) | int | `30` ×330<br>`0` ×2 |
| `start_y` | 332 | None/None (332) | int | `80` ×330<br>`50` ×2 |
| `end_x` | 332 | None/None (332) | int | `642` ×310<br>`1006` ×11<br>`946` ×9<br>`976` ×2 |
| `width` | 332 | None/None (332) | int | `612` ×310<br>`976` ×13<br>`916` ×9 |
| `height` | 332 | None/None (332) | int | `148` ×72<br>`248` ×37<br>`98` ×33<br>`198` ×32 |
| `depth` | 332 | None/None (332) | int | `1` ×332 |
| `min_top` | 104 | None/None (104) | int | `0` ×104 |

## `ui.field.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 5565 | field/None (5071), action/None (462), component/Canvas Button (20), component/Canvas Image (6) … | dict | `{}` ×3737<br>`{color,font_family,font_size,padding_left}` ×291<br>`{font_size,margin_left}` ×281<br>`{$inherited,color,font_family,font_size}` ×248 |

## `ui.holder.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 4954 | field/None (4704), action/None (249), link/None (1) | dict | `{}` ×4426<br>`{color,font_size}` ×217<br>`{flex_direction}` ×119<br>`{font_size}` ×99 |

## `ui.icon.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 250 | action/None (249), link/None (1) | dict | `{}` ×133<br>`{color}` ×116<br>`{font_size}` ×1 |

## `ui.label.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 4708 | field/None (4684), table_cell/None (24) | dict | `{}` ×3273<br>`{color,font_size,padding_left}` ×678<br>`{font_size}` ×278<br>`{$inherited,color,font_size,padding_left,padding_right}` ×217 |

## `ui.row.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 21 | relatedlist/Canvas Data Table (21) | dict | `{}` ×21 |

## `ui.header.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 45 | table_cell/None (24), relatedlist/Canvas Data Table (21) | dict | `{}` ×45 |

## `ui.row_odd.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 21 | relatedlist/Canvas Data Table (21) | dict | `{}` ×21 |

## `ui.row_even.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 21 | relatedlist/Canvas Data Table (21) | dict | `{}` ×21 |

## `ui.static_column_label.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 21 | relatedlist/Canvas Data Table (21) | dict | `{}` ×21 |

## `ui.static_column_header.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 21 | relatedlist/Canvas Data Table (21) | dict | `{}` ×21 |

## `ui.static_column_column.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 21 | relatedlist/Canvas Data Table (21) | dict | `{}` ×21 |

## `ui.static_column_column_odd.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 21 | relatedlist/Canvas Data Table (21) | dict | `{}` ×21 |

## `ui.static_column_column_even.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 21 | relatedlist/Canvas Data Table (21) | dict | `{}` ×21 |

## `ui.column.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 24 | table_cell/None (24) | dict | `{}` ×24 |

## `ui.column_odd.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 24 | table_cell/None (24) | dict | `{}` ×24 |

## `ui.column_even.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 24 | table_cell/None (24) | dict | `{}` ×24 |

## `ui.field_odd.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 24 | field/None (24) | dict | `{}` ×24 |

## `ui.field_even.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 24 | field/None (24) | dict | `{}` ×24 |

## `ui.image.style`

| key | count | hosts (type/theme) | value types | most common values |
|---|---|---|---|---|
| `default` | 6 | component/Canvas Image (6) | dict | `{src}` ×6 |