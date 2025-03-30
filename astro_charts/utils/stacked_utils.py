from typing import Dict, Any, List
from datetime import datetime, timedelta

def find_stacked_alignments(self, all_dates_list: List[Dict[str, Any]], 
                             pof_rahu_data: List[Dict[str, Any]] = None,
                             pof_regulus_data: List[Dict[str, Any]] = None,
                             pof_lord_lagna_data: List[Dict[str, Any]] = None,
                             time_window_hours: int = 12) -> List[Dict[str, Any]]:
        """
        Check if any dates in the dates list align with Part of Fortune special configurations.
        When dates are close to these special configurations, they are considered "stacked"
        and marked as more powerful.
        
        Args:
            all_dates_list: List of date dictionaries from dates_summary
            pof_rahu_data: List of Part of Fortune - Rahu conjunction data
            pof_regulus_data: List of Part of Fortune - Regulus conjunction data
            pof_lord_lagna_data: List of Part of Fortune - Lord Lagna conjunction data
            time_window_hours: Hours window to consider for alignment (default: 12 hours)
            
        Returns:
            The same dates list with added stacked_with information where applicable
        """
        try:
            # If no special configuration data provided, return original list
            if not pof_rahu_data and not pof_regulus_data and not pof_lord_lagna_data:
                return all_dates_list
                
            # Convert time window to seconds for comparison
            time_window_seconds = time_window_hours * 3600
            
            # Process each date in the list
            for date_entry in all_dates_list:
                if "date" not in date_entry or not date_entry["date"]:
                    continue
                    
                try:
                    # Parse the date string to a datetime object
                    date_datetime = datetime.strptime(date_entry["date"], "%Y-%m-%d %H:%M")
                    stacked_with = []
                    
                    # Check for Part of Fortune - Rahu conjunctions
                    if pof_rahu_data:
                        for pof_rahu in pof_rahu_data:
                            if "target_date" not in pof_rahu or "error" in pof_rahu:
                                continue
                                
                            try:
                                pof_rahu_datetime = datetime.strptime(pof_rahu["target_date"], "%Y-%m-%d %H:%M")
                                
                                # Check if within time window and is conjunct
                                time_diff = abs((date_datetime - pof_rahu_datetime).total_seconds())
                                if time_diff <= time_window_seconds and pof_rahu.get("is_pof_rahu_conjunct", False):
                                    stack_info = {
                                        "type": "part_of_fortune_rahu",
                                        "date": pof_rahu["target_date"],
                                        "description": "Part of Fortune conjunct Rahu (North Node)",
                                        "significance": "Intensifies manifestation power and karmic significance"
                                    }
                                    stacked_with.append(stack_info)
                            except Exception as e:
                                print(f"Error processing POF-Rahu date {pof_rahu.get('target_date')}: {str(e)}")
                    
                    # Check for Part of Fortune - Regulus conjunctions
                    if pof_regulus_data:
                        for pof_regulus in pof_regulus_data:
                            if "target_date" not in pof_regulus or "error" in pof_regulus:
                                continue
                                
                            try:
                                pof_regulus_datetime = datetime.strptime(pof_regulus["target_date"], "%Y-%m-%d %H:%M")
                                
                                # Check if within time window and is conjunct
                                time_diff = abs((date_datetime - pof_regulus_datetime).total_seconds())
                                if time_diff <= time_window_seconds and pof_regulus.get("is_pof_regulus_conjunct", False):
                                    stack_info = {
                                        "type": "part_of_fortune_regulus",
                                        "date": pof_regulus["target_date"],
                                        "description": "Part of Fortune conjunct Regulus (Royal Star)",
                                        "significance": "Adds fame, recognition and royal favor to manifestations"
                                    }
                                    stacked_with.append(stack_info)
                            except Exception as e:
                                print(f"Error processing POF-Regulus date {pof_regulus.get('target_date')}: {str(e)}")
                    
                    # Check for Part of Fortune - Lord Lagna conjunctions
                    if pof_lord_lagna_data:
                        for pof_lord in pof_lord_lagna_data:
                            if "target_date" not in pof_lord or "error" in pof_lord:
                                continue
                                
                            try:
                                pof_lord_datetime = datetime.strptime(pof_lord["target_date"], "%Y-%m-%d %H:%M")
                                
                                # Check if within time window and is conjunct
                                time_diff = abs((date_datetime - pof_lord_datetime).total_seconds())
                                if time_diff <= time_window_seconds and pof_lord.get("is_pof_lord_lagna_conjunct", False):
                                    lord_planet = pof_lord.get("lord_lagna", {}).get("planet", "").capitalize()
                                    stack_info = {
                                        "type": "part_of_fortune_lord_lagna",
                                        "date": pof_lord["target_date"],
                                        "description": f"Part of Fortune conjunct {lord_planet} (Lord of your Ascendant)",
                                        "significance": "Aligns personal empowerment with financial/material prosperity"
                                    }
                                    stacked_with.append(stack_info)
                            except Exception as e:
                                print(f"Error processing POF-Lord Lagna date {pof_lord.get('target_date')}: {str(e)}")
                    
                    # If we found any stacked configurations, add them to the date entry
                    if stacked_with:
                        date_entry["stacked_with"] = stacked_with
                        # Also mark the date as more powerful
                        date_entry["stacked_power"] = len(stacked_with)
                        if "significance" in date_entry:
                            date_entry["significance"] = "STACKED POWER: " + date_entry["significance"]
                        
                except Exception as e:
                    print(f"Error processing date entry {date_entry.get('date')}: {str(e)}")
            
            return all_dates_list
            
        except Exception as e:
            print(f"Error in find_stacked_alignments: {str(e)}")
            return all_dates_list  # Return original list in case of error
            
def find_internally_stacked_dates(self, all_dates_list: List[Dict[str, Any]], 
                                   exclude_same_type: bool = True) -> List[Dict[str, Any]]:
        """
        Find dates within the dates_summary that stack with each other (occur close in time).
        This identifies when multiple auspicious dates/alignments occur close to each other,
        creating a compound effect of beneficial energies.
        
        Alignments are considered stacked only if their actual time windows overlap.
        
        Args:
            all_dates_list: List of date dictionaries from dates_summary
            exclude_same_type: Whether to exclude stacking between dates of the same type
            
        Returns:
            The same dates list with added internal_stacks information where applicable
        """
        try:
            # If less than 2 dates, no stacking possible
            if len(all_dates_list) < 2:
                return all_dates_list
            
            # First filter out entries with invalid dates or "N/A"
            valid_dates = []
            for date_entry in all_dates_list:
                if "date" not in date_entry or not date_entry["date"] or "N/A" in date_entry["date"]:
                    continue
                    
                try:
                    # Check if it can be parsed as a datetime
                    datetime.strptime(date_entry["date"], "%Y-%m-%d %H:%M")
                    valid_dates.append(date_entry)
                except (ValueError, TypeError):
                    continue
            
            # Process each date in the list to find stacks
            for i, date_entry in enumerate(valid_dates):
                try:
                    # Get date entry type from its name field
                    entry_type = date_entry.get("name", "").split("_")[0] if "_" in date_entry.get("name", "") else ""
                    
                    # Get time window for this entry
                    entry_start_time = None
                    entry_end_time = None
                    
                    # Try to get precise start/end times from duration if available
                    if "duration" in date_entry and date_entry["duration"] and isinstance(date_entry["duration"], dict):
                        if "start_time" in date_entry["duration"] and "end_time" in date_entry["duration"]:
                            try:
                                entry_start_time = datetime.strptime(date_entry["duration"]["start_time"], "%Y-%m-%d %H:%M")
                                entry_end_time = datetime.strptime(date_entry["duration"]["end_time"], "%Y-%m-%d %H:%M")
                            except (ValueError, TypeError):
                                pass
                    
                    # Fallback to exact time if start/end times not available directly
                    if not entry_start_time or not entry_end_time:
                        # For alignments with days duration
                        if "duration" in date_entry and date_entry["duration"] and isinstance(date_entry["duration"], dict) and "days" in date_entry["duration"]:
                            if date_entry["duration"]["days"] > 0 and "start_date" in date_entry["duration"] and "end_date" in date_entry["duration"]:
                                if date_entry["duration"]["start_date"] != "N/A" and date_entry["duration"]["end_date"] != "N/A":
                                    try:
                                        # Try to parse with time if available, otherwise use date only
                                        try:
                                            entry_start_time = datetime.strptime(date_entry["duration"]["start_date"], "%Y-%m-%d %H:%M")
                                        except ValueError:
                                            entry_start_time = datetime.strptime(date_entry["duration"]["start_date"], "%Y-%m-%d")
                                            
                                        try:
                                            entry_end_time = datetime.strptime(date_entry["duration"]["end_date"], "%Y-%m-%d %H:%M")
                                        except ValueError:
                                            # Add 23:59 to make it end of day
                                            end_date_str = date_entry["duration"]["end_date"] + " 23:59"
                                            entry_end_time = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M")
                                    except (ValueError, TypeError):
                                        pass
                    
                    # If still no duration info, use exact time and default to a small window (±5 minutes)
                    if not entry_start_time or not entry_end_time:
                        try:
                            exact_time = datetime.strptime(date_entry["date"], "%Y-%m-%d %H:%M")
                            entry_start_time = exact_time - timedelta(minutes=5)
                            entry_end_time = exact_time + timedelta(minutes=5)
                        except (ValueError, TypeError):
                            # If we can't determine a time window, skip this entry
                            continue
                    
                    internal_stacks = []
                    
                    # Check other dates for stacking
                    for j, other_entry in enumerate(valid_dates):
                        if i == j:  # Skip self
                            continue
                            
                        # Get other entry type
                        other_type = other_entry.get("name", "").split("_")[0] if "_" in other_entry.get("name", "") else ""
                        
                        # If excluding same type and types match, skip
                        if exclude_same_type and entry_type and other_type and entry_type == other_type:
                            continue
                            
                        try:
                            # Get time window for other entry
                            other_start_time = None
                            other_end_time = None
                            
                            # Try to get precise start/end times from duration if available
                            if "duration" in other_entry and other_entry["duration"] and isinstance(other_entry["duration"], dict):
                                if "start_time" in other_entry["duration"] and "end_time" in other_entry["duration"]:
                                    try:
                                        other_start_time = datetime.strptime(other_entry["duration"]["start_time"], "%Y-%m-%d %H:%M")
                                        other_end_time = datetime.strptime(other_entry["duration"]["end_time"], "%Y-%m-%d %H:%M")
                                    except (ValueError, TypeError):
                                        pass
                            
                            # Fallback to exact time if start/end times not available directly
                            if not other_start_time or not other_end_time:
                                # For alignments with days duration
                                if "duration" in other_entry and other_entry["duration"] and isinstance(other_entry["duration"], dict) and "days" in other_entry["duration"]:
                                    if other_entry["duration"]["days"] > 0 and "start_date" in other_entry["duration"] and "end_date" in other_entry["duration"]:
                                        if other_entry["duration"]["start_date"] != "N/A" and other_entry["duration"]["end_date"] != "N/A":
                                            try:
                                                # Try to parse with time if available, otherwise use date only
                                                try:
                                                    other_start_time = datetime.strptime(other_entry["duration"]["start_date"], "%Y-%m-%d %H:%M")
                                                except ValueError:
                                                    other_start_time = datetime.strptime(other_entry["duration"]["start_date"], "%Y-%m-%d")
                                                    
                                                try:
                                                    other_end_time = datetime.strptime(other_entry["duration"]["end_date"], "%Y-%m-%d %H:%M")
                                                except ValueError:
                                                    # Add 23:59 to make it end of day
                                                    other_end_date_str = other_entry["duration"]["end_date"] + " 23:59"
                                                    other_end_time = datetime.strptime(other_end_date_str, "%Y-%m-%d %H:%M")
                                            except (ValueError, TypeError):
                                                pass
                            
                            # If still no duration info, use exact time and default to a small window (±5 minutes)
                            if not other_start_time or not other_end_time:
                                try:
                                    other_exact_time = datetime.strptime(other_entry["date"], "%Y-%m-%d %H:%M")
                                    other_start_time = other_exact_time - timedelta(minutes=5)
                                    other_end_time = other_exact_time + timedelta(minutes=5)
                                except (ValueError, TypeError):
                                    # If we can't determine a time window, skip this entry
                                    continue
                            
                            # Check if the time windows overlap
                            if entry_start_time <= other_end_time and entry_end_time >= other_start_time:
                                # Calculate overlap amount in minutes
                                overlap_start = max(entry_start_time, other_start_time)
                                overlap_end = min(entry_end_time, other_end_time)
                                overlap_minutes = (overlap_end - overlap_start).total_seconds() / 60
                                
                                # Only consider it a stack if there's a meaningful overlap (at least 1 minute)
                                if overlap_minutes >= 1:
                                    # Found a stacked date with overlapping time window
                                    stack_info = {
                                        "type": "internal_stack",
                                        "name": other_entry.get("name", "unknown"),
                                        "date": other_entry["date"],
                                        "description": other_entry.get("description", "Stacked alignment"),
                                        "overlap_minutes": round(overlap_minutes, 1),
                                        "overlap_window": {
                                            "start_time": overlap_start.strftime("%Y-%m-%d %H:%M"),
                                            "end_time": overlap_end.strftime("%Y-%m-%d %H:%M"),
                                            "description": f"Alignments overlap for {round(overlap_minutes)} minutes from {overlap_start.strftime('%H:%M')} to {overlap_end.strftime('%H:%M')}"
                                        }
                                    }
                                    
                                    # Add duration if available
                                    if "duration" in other_entry and other_entry["duration"]:
                                        stack_info["duration"] = other_entry["duration"]
                                        
                                    internal_stacks.append(stack_info)
                        except Exception as e:
                            print(f"Error comparing with date {other_entry.get('date')}: {str(e)}")
                    
                    # If we found any internal stacks, add them to the date entry
                    if internal_stacks:
                        if "stacked_with" not in date_entry:
                            date_entry["stacked_with"] = []
                            
                        # Add internal stacks to any existing stacked_with array
                        date_entry["stacked_with"].extend(internal_stacks)
                        
                        # Update or set stacked_power
                        if "stacked_power" in date_entry:
                            date_entry["stacked_power"] += len(internal_stacks)
                        else:
                            date_entry["stacked_power"] = len(internal_stacks)
                            
                        # Update significance to indicate stacking
                        if "significance" in date_entry:
                            if "STACKED POWER:" not in date_entry["significance"]:
                                date_entry["significance"] = "STACKED POWER: " + date_entry["significance"]
                        else:
                            date_entry["significance"] = "STACKED POWER: Multiple alignments overlap with this period"
                        
                except Exception as e:
                    print(f"Error processing internal stacking for {date_entry.get('date')}: {str(e)}")
            
            return all_dates_list
            
        except Exception as e:
            print(f"Error in find_internally_stacked_dates: {str(e)}")
            return all_dates_list  # Return original list in case of error
