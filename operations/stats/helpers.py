def plot_histogram(df, column, plotting_pane, x_range=None):
    """
    Helper function to plot histogram of a numeric variable
    in the provided x_range onto the panel plotting pane.
    """
    fig, ax = plt.subplots(1,1)
    df[column].plot.hist(bins=50, ax=ax, title = 'Histogram of: ' + column, xlim=x_range)
    ax.set_xlabel(column)
    plotting_pane.object = fig
    plt.close()

def b(event):
    """
    Updates bin sliders when "next" is clicked
    """
    if next_bin.clicks == 0:
        return
    
    selected_col = binnable.value[next_var.clicks]

    if next_bin.clicks < num.value:
        bin_range.name = 'Select Range for Bin #' + str(next_bin.clicks + 1)
        selected_bins[next_var.clicks].append(bin_range.value)
        bin_range.start = bin_range.value[1] + 1
        bin_range.value = (bin_range.value[1] + 1, df[selected_col].max())
        plot_histogram(df, selected_col, plot, x_range = bin_range.value)
    else:
        selected_bins[next_var.clicks].append(bin_range.value)
        next_bin.disabled = True
        
        if selected_col != binnable.value[-1]:
            layout[0][4] = next_var
        else:
            layout[0][4] = "Variable Binning Complete!"

def c(event):
    """
    Resets layout when "continue" is clicked
    """
    next_bin.clicks = 0
    next_col = binnable.value[next_var.clicks] 
    text.value = next_col
    num.value = 1
    bin_range.start = df[next_col].min()
    bin_range.end = df[next_col].max()
    bin_range.value = (df[next_col].min(), df[next_col].max())
    next_bin.disabled = False
    layout[0][4] = ""
    plot_histogram(df, next_col, plot)

def find_unique(var):
    """
    Helper function to return all unique entries for #multi survey variables
    """
    arr = df[var].unique()
    all_entries = set()
    for i in range(len(arr)):
        if arr[i] != arr[i]:
            continue
        if (i != 0) and ('|' in arr[i]):
            arr[i] = arr[i].split('|')
            for j in arr[i]:
                all_entries.add(j)
        else:
            all_entries.add(arr[i])
    all_entries = list(all_entries)
    return all_entries

def find_tags(value):
    """
    Helper function to extract SuAVE qualifiers from variable names
    """
    tags = re.findall('#\S+', value)
    if tags == []:
        return ['untagged']
    return tags

def find_factor_contributions(var, var_level, filter_vars):
    """
    Helper function to find all the factor contributions from
    a list of filter variables at the level of the variable of interest.
    """
    out = {var: {}}
    
    for f in filter_vars:
        if var == f:
            continue                    
        if '#multi' in f:
            a_levels = find_unique(f)
        else:
            a_levels = df[f].value_counts().index.to_list()
        level_name = var + '_' + str(var_level)
        if (level_name) not in out[var].keys():
            out[var][level_name] = {}
            
        for j in a_levels:
            x_count = df[df[var]==var_level].shape[0]
            x_prop = df[df[var]==var_level].shape[0]/df.shape[0]
            a_count = df[df[f]==j].shape[0]
            ax_count = df[(df[f]==j) & (df[var]==var_level)].shape[0]
            try:
                ax_prop = ax_count/a_count
                completeness = round((ax_count/x_count)*100, 3)
            except:
                ax_prop = 0
                completeness = 0
            contribution = round((ax_prop - x_prop)*100, 3)
            accuracy = round(ax_prop*100, 3)
            value_name = f.split('#')[0] + ': ' + str(j)
            out[var][level_name][value_name] = [accuracy,completeness,contribution,a_count,ax_count,find_tags(f)]

    return out

def sort_contributions(dictionary, ascending=True):
    """
    Helper function to sort dictionary by values in ascending/descending order
    """
    out_dict = dictionary[selector.value]
    for key in out_dict.keys():
        out_dict[key] = {k: v for k, v in sorted(out_dict[key].items(), key=lambda x: x[1], reverse=ascending)}
    return out_dict

def color(val):
    """
    Syling function to change color of scalar values
    """
    color = 'red' if val < 0 else 'green'
    return 'color: %s' % color

def filter_counts(df):
    """
    Helper function to remove 0 counts from output dataframe
    """
    df = df[df['Completeness'] > 0]
    return df

def search_filter(df, pattern, column):
    """
    Helper function to filter dataframe values from text input
    """
    if not pattern:
        return df
    return df[df[column].str.contains(pattern, case=False)]

@pn.depends(name=filename, watch=True)
def file_download(name):
    download.filename = name